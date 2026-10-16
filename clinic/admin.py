from django.contrib import admin
from .models import Specialty,Insurance,PatientProfile,Doctor,Slot,Appointment
admin.site.register([Specialty,Insurance,PatientProfile,Doctor,Slot,Appointment])
