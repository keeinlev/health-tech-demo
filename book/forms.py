from django import forms
from accounts.models import User, Doctor, DoctorInfo, Patient, PatientInfo
from .times import IntTimes
from .models import Appointment
from django.core.exceptions import ValidationError

class BookForm(forms.Form):
    date = forms.DateField(label=False, required=True, widget=forms.DateInput(attrs={'type': "date", 'class': "form-control", 'id': "datetime", 'placeholder': "2020-02-20", 'max':"9999-12-31"}))
    time = forms.TimeField(label=False, required=True)
    doctor = forms.ModelChoiceField(label=False, queryset=Doctor.objects.all(), widget=forms.RadioSelect(attrs={'type': "radio", 'class': 'doctor-radio'}))
    
    
    #fields = ['datetime', 'consultation', 'patient', 'doctor']

class CreateAppointmentForm(forms.ModelForm):
    time = forms.ChoiceField(label=False, choices=IntTimes.choices, widget=forms.Select(attrs={'class':'custom-select time-input'}))
    class Meta:
        model = Appointment
        fields = ['date', 'time']
        widgets = {'date': forms.HiddenInput()}
    
    def clean(self):

        cleaned_data = self.cleaned_data
        try:
           Appointment.objects.get(date=cleaned_data['date'], time=cleaned_data['time'])
        except Appointment.DoesNotExist:
           pass
        else:
           raise ValidationError('Appointment already exists!')

        # Always return cleaned_data
        return cleaned_data

class CreateAppointmentRangeForm(forms.Form):
    startdate = forms.DateField(label=False, required=True, widget=forms.DateInput(attrs={'type': "date", 'class': "form-control", 'placeholder': "2020-02-20", 'max':"9999-12-31"}))
    starttime = forms.ChoiceField(label=False, required=True, choices=IntTimes.choices, widget=forms.Select(attrs={'class':'custom-select'}))
    enddate = forms.DateField(label=False, required=True, widget=forms.DateInput(attrs={'type': "date", 'class': "form-control", 'placeholder': "2020-02-20", 'max':"9999-12-31"}))
    endtime = forms.ChoiceField(label=False, required=True, choices=IntTimes.choices, widget=forms.Select(attrs={'class':'custom-select'}))

class CancelAppointmentRangeForm(forms.Form):
    c_startdate = forms.DateField(label=False, required=True, widget=forms.DateInput(attrs={'type': "date", 'class': "form-control", 'placeholder': "2020-02-20", 'max':"9999-12-31"}))
    c_starttime = forms.ChoiceField(label=False, required=True, choices=IntTimes.choices, widget=forms.Select(attrs={'class':'custom-select'}))
    c_enddate = forms.DateField(label=False, required=True, widget=forms.DateInput(attrs={'type': "date", 'class': "form-control", 'placeholder': "2020-02-20", 'max':"9999-12-31"}))
    c_endtime = forms.ChoiceField(label=False, required=True, choices=IntTimes.choices, widget=forms.Select(attrs={'class':'custom-select'}))

class EditAppointmentForm(forms.Form):
    doctor = forms.ModelChoiceField(label=False, queryset=Doctor.objects.all(), required=True, widget=forms.HiddenInput())
    date = forms.DateField(label=False, required=True, widget=forms.HiddenInput())
    time = forms.ChoiceField(label=False, required=True, choices=IntTimes.choices, widget=forms.Select(attrs={'class':'custom-select'}))
    consultation = forms.CharField(label=False, max_length=100, required=True, widget=forms.Select(attrs={'class':'custom-select'}))

class CancelConfirmForm(forms.Form):
    doctor = forms.ModelChoiceField(label=False, queryset=Doctor.objects.all(), required=True, widget=forms.HiddenInput())
    patient = forms.ModelChoiceField(label=False, queryset=Patient.objects.all(), required=True, widget=forms.HiddenInput())
    date = forms.DateField(label=False, required=True, widget=forms.HiddenInput())
    time = forms.ChoiceField(label=False, required=True, choices=IntTimes.choices, widget=forms.HiddenInput())
    reason = forms.CharField(label=False, required=True, widget=forms.Textarea)