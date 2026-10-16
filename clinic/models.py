from django.db import models
from django.contrib.auth.models import User

class Specialty(models.Model):
    name=models.CharField(max_length=100,unique=True)
    def __str__(self): 
        return self.name

class Insurance(models.Model):
    name=models.CharField(max_length=100,unique=True)
    coverage_notes=models.TextField(help_text='Informational only; verify eligibility with insurer.')
    def __str__(self): 
        return self.name

class PatientProfile(models.Model):
    user=models.OneToOneField(User,on_delete=models.CASCADE,related_name='patient_profile')
    phone=models.CharField(max_length=30,blank=True)
    insurance=models.ForeignKey(Insurance,on_delete=models.SET_NULL,null=True,blank=True)
    def __str__(self): 
        return self.user.username

class Doctor(models.Model):
    user=models.OneToOneField(User,on_delete=models.CASCADE,related_name='doctor_profile')
    specialty=models.ForeignKey(Specialty,on_delete=models.PROTECT)
    bio=models.CharField(max_length=250,blank=True)
    def __str__(self): 
        return f'Dr. {self.user.get_full_name() or self.user.username}'

class Slot(models.Model):
    doctor=models.ForeignKey(Doctor,on_delete=models.CASCADE,related_name='slots')
    starts_at=models.DateTimeField()
    ends_at=models.DateTimeField()
    class Meta:
        ordering=['starts_at']
        constraints=[models.UniqueConstraint(
            fields=['doctor','starts_at'],
            name='unique_doctor_slot'
            )
        ]
    def __str__(self): 
        return f'{self.doctor} - {self.starts_at}'

class Appointment(models.Model):
    STATUS=[('booked','Booked'),('completed','Completed'),('cancelled','Cancelled')]
    patient=models.ForeignKey(User,on_delete=models.CASCADE,related_name='appointments')
    slot=models.ForeignKey(Slot,on_delete=models.PROTECT,related_name='appointments')
    status=models.CharField(max_length=12,choices=STATUS,default='booked')
    reason=models.CharField(max_length=200,blank=True)
    created_at=models.DateTimeField(auto_now_add=True)
    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['slot'],
                condition=models.Q(status__in=['booked', 'completed']),
                name='unique_active_appointment_per_slot',
            )
        ]
    def __str__(self): 
        return f'{self.patient.username}: {self.slot}'
