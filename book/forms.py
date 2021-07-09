from django import forms
from accounts.models import User, Doctor, DoctorInfo, Patient, PatientInfo
from .times import IntTimes
from .models import Appointment
from django.core.exceptions import ValidationError

class CreateAppointmentForm(forms.ModelForm):
    time = forms.ChoiceField(label=False, choices=IntTimes.choices, widget=forms.Select(attrs={'class':'custom-select time-input'}))
    class Meta:
        model = Appointment
        fields = ['date', 'time', 'doctor']
        widgets = {'date': forms.HiddenInput(), 'doctor': forms.HiddenInput()}
    
    def clean(self):

        cleaned_data = self.cleaned_data
        try:
           Appointment.objects.get(date=cleaned_data['date'], time=cleaned_data['time'], doctor=cleaned_data['doctor'])
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
    c_startdate = forms.DateField(label=False, required=True, widget=forms.DateInput(attrs={'type': "date", 'class': "form-control cancel-mult-fields", 'placeholder': "2020-02-20", 'max':"9999-12-31"}))
    c_starttime = forms.ChoiceField(label=False, required=True, choices=IntTimes.choices, widget=forms.Select(attrs={'class':'custom-select cancel-mult-fields'}))
    c_enddate = forms.DateField(label=False, required=True, widget=forms.DateInput(attrs={'type': "date", 'class': "form-control cancel-mult-fields", 'placeholder': "2020-02-20", 'max':"9999-12-31"}))
    c_endtime = forms.ChoiceField(label=False, required=True, choices=IntTimes.choices, widget=forms.Select(attrs={'class':'custom-select cancel-mult-fields'}))
    reason = forms.CharField(label=False, required=True, widget=forms.TextInput(attrs={"class":"form-control", "onkeypress":"return event.charCode != 96"}))

class EditAppointmentForm(forms.Form):
    doctor = forms.ModelChoiceField(label=False, queryset=Doctor.objects.all(), required=True, widget=forms.HiddenInput())
    date = forms.DateField(label=False, required=True, widget=forms.HiddenInput())
    time = forms.ChoiceField(label=False, required=True, choices=IntTimes.choices, widget=forms.Select(attrs={'class':'custom-select'}))
    consultation = forms.CharField(label=False, max_length=100, required=True, widget=forms.Select(attrs={'class':'custom-select'}))
    appt_type = forms.BooleanField(label=False, required=False, widget=forms.CheckboxInput(attrs={'data-toggle':'toggle', 'data-on': 'Video', 'data-off': 'Phone', 'data-onstyle':'success', 'data-offstyle':'primary'}))

class CancelConfirmForm(forms.Form):
    doctor = forms.ModelChoiceField(label=False, queryset=Doctor.objects.all(), required=True, widget=forms.HiddenInput())
    patient = forms.ModelChoiceField(label=False, queryset=Patient.objects.all(), required=True, widget=forms.HiddenInput())
    date = forms.DateField(label=False, required=True, widget=forms.HiddenInput())
    time = forms.ChoiceField(label=False, required=True, choices=IntTimes.choices, widget=forms.HiddenInput())
    reason = forms.CharField(label=False, required=True, widget=forms.Textarea)