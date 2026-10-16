from django.urls import path
from django.contrib.auth import views as auth_views
from . import views
urlpatterns=[
 path('',views.home,name='home'),path('insurance/',views.insurance_info,name='insurance_info'),path('profile/',views.edit_profile,name='edit_profile'),path('register/',views.register,name='register'),
 path('login/',auth_views.LoginView.as_view(template_name='login.html'),name='login'),
 path('logout/',auth_views.LogoutView.as_view(),name='logout'),
 path('dashboard/',views.dashboard,name='dashboard'),path('doctors/',views.doctors,name='doctors'),
 path('doctors/<int:doctor_id>/',views.doctor_slots,name='doctor_slots'),
 path('book/<int:slot_id>/',views.book,name='book'),
 path('appointment/<int:appointment_id>/cancel/',views.cancel_appointment,name='cancel_appointment'),
 path('appointment/<int:appointment_id>/reschedule/',views.patient_reschedule,name='patient_reschedule'),
 path('doctor/dashboard/',views.doctor_dashboard,name='doctor_dashboard'),
 path('doctor/reschedule/<int:appointment_id>/',views.reschedule,name='reschedule'),
 path('doctor/complete/<int:appointment_id>/',views.complete,name='complete'),
 path('ai/suggest/',views.ai_api,name='ai_api'),
]
