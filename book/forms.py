from django import forms
from accounts.models import User, Doctor, DoctorInfo, Patient, PatientInfo
from .times import IntTimes
from .models import Appointment
from django.core.exceptions import ValidationError

class EditAppointmentForm(forms.Form):
    doctor = forms.ModelChoiceField(label=False, queryset=Doctor.objects.all(), required=True, widget=forms.HiddenInput())
    date = forms.DateField(label=False, required=True, widget=forms.HiddenInput())
    time = forms.ChoiceField(label=False, required=True, choices=IntTimes.choices, widget=forms.Select(attrs={'class':'custom-select'}))
    consultation = forms.CharField(label=False, max_length=100, required=True, widget=forms.Select(attrs={'class':'custom-select'}))
    appt_type = forms.ChoiceField(label=False, required=False, widget=forms.RadioSelect(), choices=[(0,'Phone'), (1, 'Video')])

class CancelConfirmForm(forms.Form):
    doctor = forms.ModelChoiceField(label=False, queryset=Doctor.objects.all(), required=True, widget=forms.HiddenInput())
    patient = forms.ModelChoiceField(label=False, queryset=Patient.objects.all(), required=True, widget=forms.HiddenInput())
    date = forms.DateField(label=False, required=True, widget=forms.HiddenInput())
    time = forms.ChoiceField(label=False, required=True, choices=IntTimes.choices, widget=forms.HiddenInput())
    reason = forms.CharField(label=False, required=True, widget=forms.Textarea)
