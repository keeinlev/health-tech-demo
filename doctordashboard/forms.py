from django import forms
from accounts.models import User, Doctor, DoctorInfo, Patient, PatientInfo
from book.times import IntTimes
from book.models import Appointment
from django.core.exceptions import ValidationError
from health.form_elements import customTextInputWidget, customDateInputWidget

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
    startdate = forms.DateField(label=False, required=True, widget=customDateInputWidget("Start"))
    starttime = forms.ChoiceField(label=False, required=True, choices=IntTimes.choices, widget=forms.Select(attrs={'class':'custom-select'}))
    enddate = forms.DateField(label=False, required=True, widget=customDateInputWidget("End"))
    endtime = forms.ChoiceField(label=False, required=True, choices=IntTimes.choices, widget=forms.Select(attrs={'class':'custom-select'}))

class CancelAppointmentRangeForm(forms.Form):
    c_startdate = forms.DateField(label=False, required=True, widget=customDateInputWidget("Start", extra_classes="cancel-mult-fields"))
    c_starttime = forms.ChoiceField(label=False, required=True, choices=IntTimes.choices, widget=forms.Select(attrs={'class':'custom-select cancel-mult-fields'}))
    c_enddate = forms.DateField(label=False, required=True, widget=customDateInputWidget("End", extra_classes="cancel-mult-fields"))
    c_endtime = forms.ChoiceField(label=False, required=True, choices=IntTimes.choices, widget=forms.Select(attrs={'class':'custom-select cancel-mult-fields'}))
    reason = forms.CharField(label=False, required=True, widget=customTextInputWidget("text", "Reason", '', exargs={"onkeypress":"return event.charCode != 96"}))
class ApptHistoryDownloadForm(forms.Form):
    FIELDS_OPTIONS = (
        ('DATE', 'Date'),
        ('TIME', 'Time'),
        ('CONS', 'Consultation'),
        ('P_NAME', 'Patient Name'),
        ('P_DOB', 'Patient DOB'),
        ('P_ADD', 'Patient Address'),
        ('P_EMAIL', 'Patient Email'),
        ('P_PHONE', 'Patient Phone #'),
        ('P_OHIP', 'Patient OHIP'),
        ('P_OHIPEX', 'Patient OHIP Expiry'),
        ('P_PHAR', 'Patient Pharmacy'),
        ('NOTES', 'Doctor Notes'),
        ('PRESC', 'Prescription'),
    )
    FORMAT_OPTIONS = (
        ('csv', '.csv'),
        ('xls', '.xls'),
    )

    startdate = forms.DateField(label=False, required=False, widget=customDateInputWidget("Start"))
    starttime = forms.ChoiceField(label=False, required=False, choices=IntTimes.choices, widget=forms.Select(attrs={'class':'custom-select dl_time'}))
    enddate = forms.DateField(label=False, required=True, widget=customDateInputWidget("End"))
    endtime = forms.ChoiceField(label=False, required=False, choices=IntTimes.choices, widget=forms.Select(attrs={'class':'custom-select dl_time'}))
    patient_search = forms.CharField(label=False, required=False, widget=customTextInputWidget("text", "Search", ''))
    fields = forms.MultipleChoiceField(label=False, required=True, choices=FIELDS_OPTIONS, widget=forms.CheckboxSelectMultiple(attrs={'checked':''}))
    fileformat = forms.ChoiceField(label=False, required=True, choices=FORMAT_OPTIONS, widget=forms.RadioSelect())
    entire_day = forms.BooleanField(label=False, required=False, widget=forms.CheckboxInput(attrs={'data-toggle':'toggle', 'data-onstyle':'success', 'data-offstyle':'secondary'}))