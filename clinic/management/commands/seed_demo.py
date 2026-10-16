from datetime import timedelta
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.utils import timezone
from clinic.models import Specialty,Insurance,Doctor,Slot

class Command(BaseCommand):
    help = 'Create safe example doctors, insurance plans, and future appointment slots.'

    def handle(self,*args,**options):
        descriptions={
            'Orthopedics':'Bones, joints and sports injuries',
            'Dermatology':'Skin and hair care',
            'Cardiology':'Heart health',
            'Ophthalmology':'Eye and vision care',
            'Dentistry':'Dental care',
            'General Medicine':'General health consultations',
        }
        for name in descriptions:
            Specialty.objects.get_or_create(name=name)
        for name,notes in [
            ('Example Basic Plan','Example only: outpatient consultation may require co-payment. Confirm with insurer.'),
            ('Example Plus Plan','Example only: specialist visits may require prior approval. Confirm with insurer.'),
            ('Self Pay','Patient pays directly; ask the clinic about fees before booking.'),
        ]:
            Insurance.objects.get_or_create(name=name,defaults={'coverage_notes':notes})
        samples=[('dr_sara','Sara','Haddad','Orthopedics'),('dr_omar','Omar','Khalil','Cardiology'),('dr_lina','Lina','Mansour','Dermatology'),('dr_yousef','Yousef','Nasser','General Medicine'),('dr_maya','Maya','Saleh','Ophthalmology'),('dr_ahmad','Ahmad','Hassan','Dentistry')]
        for username,first,last,specialty in samples:
            user,created=User.objects.get_or_create(username=username,defaults={'first_name':first,'last_name':last,'is_active':True})
            if created:
                user.set_unusable_password()
                user.save(update_fields=['password'])
            doctor,_=Doctor.objects.get_or_create(user=user,defaults={'specialty':Specialty.objects.get(name=specialty),'bio':descriptions[specialty]+' · Sample doctor profile'})
            for day in range(1,8):
                for hour in [9,10,11,14,15]:
                    start=(timezone.localtime(timezone.now())+timedelta(days=day)).replace(hour=hour,minute=0,second=0,microsecond=0)
                    Slot.objects.get_or_create(doctor=doctor,starts_at=start,defaults={'ends_at':start+timedelta(minutes=30)})
        self.stdout.write(self.style.SUCCESS('Demo content created. Doctor accounts have unusable passwords; set passwords via Django Admin for doctor login.'))
