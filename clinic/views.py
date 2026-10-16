from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.db import transaction,IntegrityError
from django.http import JsonResponse,HttpResponseForbidden
from django.shortcuts import render,redirect,get_object_or_404
from django.utils import timezone
from django.views.decorators.http import require_POST
from .models import Specialty,Doctor,Slot,Appointment,PatientProfile
from .forms import RegisterForm
from .ai_assistant import suggest_specialty

def home(request):
    return render(request,'home.html',{'specialties':Specialty.objects.all()[:6]})

def insurance_info(request):
    from .models import Insurance
    return render(request,'insurance.html',{'plans':Insurance.objects.all()})

@login_required
def edit_profile(request):
    from .forms import PatientProfileForm
    profile, _ = PatientProfile.objects.get_or_create(user=request.user)
    form = PatientProfileForm(request.POST or None,instance=profile)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request,'Profile updated.')
        return redirect('dashboard')
    return render(request,'profile.html',{'form':form})

def register(request):
    form=RegisterForm(request.POST or None)
    if request.method=='POST' and form.is_valid():
        user=form.save(),
        login(request,user),
        return redirect('dashboard')
    return render(request,'register.html',{'form':form})

@login_required
def dashboard(request):
    if Doctor.objects.filter(user=request.user).exists(): return redirect('doctor_dashboard')
    appointments=Appointment.objects.filter(patient=request.user).select_related('slot__doctor__user').order_by('slot__starts_at')
    available_slots = Slot.objects.filter(
        doctor__in=Doctor.objects.filter(slots__appointments__patient=request.user, slots__appointments__status='booked'),
        starts_at__gt=timezone.now()
    ).exclude(appointments__status__in=['booked', 'completed']).distinct().order_by('starts_at')
    return render(request,'dashboard.html',{
        'appointments':appointments,
        'available_slots':available_slots,
        'profile':PatientProfile.objects.filter(user=request.user).select_related('insurance').first()
    })

@login_required
def doctors(request):
    specialties=Specialty.objects.all()
    specialty_id=request.GET.get('specialty')
    queryset=Doctor.objects.select_related('user','specialty')
    if specialty_id and specialty_id.isdigit(): queryset=queryset.filter(specialty_id=int(specialty_id))
    return render(request,'doctors.html',{'doctors':queryset,'specialties':specialties,'selected':specialty_id})

@login_required
def doctor_slots(request,doctor_id):
    doctor=get_object_or_404(Doctor.objects.select_related('user','specialty'),pk=doctor_id)
    slots=Slot.objects.filter(doctor=doctor,starts_at__gte=timezone.now()).exclude(appointments__status__in=['booked', 'completed']).order_by('starts_at')
    return render(request,'slots.html',{'doctor':doctor,'slots':slots})

@login_required
@require_POST
def book(request,slot_id):
    if Doctor.objects.filter(user=request.user).exists(): return HttpResponseForbidden('Doctor accounts cannot book as patients.')
    try:
        with transaction.atomic():
            slot=get_object_or_404(Slot.objects.select_for_update(),pk=slot_id,starts_at__gt=timezone.now())
            if Appointment.objects.filter(slot=slot,status__in=['booked','completed']).exists():
                messages.error(request,'This slot is already booked.')
                return redirect('doctor_slots',doctor_id=slot.doctor_id)
            Appointment.objects.create(patient=request.user,slot=slot)
    except IntegrityError:
        messages.error(request,'This slot was booked by another patient.')
        return redirect('doctors')
    messages.success(request,'Your appointment is confirmed!')
    return redirect('dashboard')

@login_required
@require_POST
def cancel_appointment(request, appointment_id):
    # Only the patient who owns the appointment may cancel it.
    appointment = get_object_or_404(
        Appointment, pk=appointment_id, patient=request.user, status='booked'
    )
    if appointment.slot.starts_at <= timezone.now():
        messages.error(request, 'Past appointments cannot be cancelled.')
    else:
        appointment.status = 'cancelled'
        appointment.save(update_fields=['status'])
        messages.success(request, 'Appointment cancelled. The time is available again.')
    return redirect('dashboard')


@login_required
@require_POST
def patient_reschedule(request, appointment_id):
    appointment = get_object_or_404(
        Appointment.objects.select_related('slot'),
        pk=appointment_id, patient=request.user, status='booked'
    )
    if appointment.slot.starts_at <= timezone.now():
        messages.error(request, 'Past appointments cannot be rescheduled.')
        return redirect('dashboard')
    new_slot = get_object_or_404(
        Slot, pk=request.POST.get('slot_id'),
        doctor=appointment.slot.doctor, starts_at__gt=timezone.now()
    )
    try:
        with transaction.atomic():
            if Appointment.objects.filter(
                slot=new_slot, status__in=['booked', 'completed']
            ).exists():
                messages.error(request, 'This time is no longer available.')
            else:
                appointment.slot = new_slot
                appointment.save(update_fields=['slot'])
                messages.success(request, 'Your appointment was rescheduled.')
    except IntegrityError:
        messages.error(request, 'Another patient just booked that time.')
    return redirect('dashboard')


@login_required
def doctor_dashboard(request):
    doctor=get_object_or_404(Doctor,user=request.user)
    appointments=Appointment.objects.filter(slot__doctor=doctor).select_related('patient','slot').order_by('slot__starts_at')
    slots=Slot.objects.filter(doctor=doctor,starts_at__gt=timezone.now()).exclude(appointments__status__in=['booked', 'completed'])
    return render(request,'doctor_dashboard.html',{'appointments':appointments,'slots':slots})

@login_required
@require_POST
def reschedule(request,appointment_id):
    doctor=get_object_or_404(Doctor,user=request.user)
    appointment=get_object_or_404(Appointment,pk=appointment_id,slot__doctor=doctor,status='booked')
    new_slot=get_object_or_404(Slot,pk=request.POST.get('slot_id'),doctor=doctor,starts_at__gt=timezone.now())
    try:
        with transaction.atomic():
            if Appointment.objects.filter(slot=new_slot,status__in=['booked','completed']).exists():
                messages.error(request,'Slot unavailable.')
            else:
                appointment.slot=new_slot
                appointment.save(update_fields=['slot'])
                messages.success(request,'Appointment rescheduled.')
    except IntegrityError: messages.error(request,'Slot was just taken.')
    return redirect('doctor_dashboard')

@login_required
@require_POST
def complete(request,appointment_id):
    doctor=get_object_or_404(Doctor,user=request.user)
    appointment=get_object_or_404(Appointment,pk=appointment_id,slot__doctor=doctor,status='booked')
    appointment.status='completed';appointment.save(update_fields=['status'])
    messages.success(request,'Visit marked completed.')
    return redirect('doctor_dashboard')

@login_required
@require_POST
def ai_api(request):
    text=request.POST.get('message','')[:500]
    specialty=suggest_specialty(text,Specialty.objects.values_list('name',flat=True))
    return JsonResponse({'specialty':specialty,'message':('Suggested specialty: '+specialty) if specialty else 'Please select a specialty manually. This assistant does not provide medical diagnoses.'})
