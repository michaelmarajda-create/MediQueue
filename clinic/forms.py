from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import PatientProfile,Insurance
class RegisterForm(UserCreationForm):
    email=forms.EmailField(required=True)
    first_name=forms.CharField(max_length=150)
    last_name=forms.CharField(max_length=150)
    phone=forms.CharField(max_length=30,required=False)
    insurance=forms.ModelChoiceField(queryset=Insurance.objects.all(),required=False)
    class Meta:
        model=User
        fields=['username','first_name','last_name','email','password1','password2']
    def clean_email(self):
        email=self.cleaned_data['email']
        if User.objects.filter(email__iexact=email).exists(): raise forms.ValidationError('Email already registered.')
        return email
    def save(self,commit=True):
        user=super().save(commit=commit)
        if commit: PatientProfile.objects.create(user=user,phone=self.cleaned_data['phone'],insurance=self.cleaned_data['insurance'])
        return user

class PatientProfileForm(forms.ModelForm):
    class Meta:
        model=PatientProfile
        fields=['phone','insurance']
