from django import forms
from .models import User


class SignUpForm(forms.Form):
    first_name = forms.CharField(label=False, max_length=30, required=True, widget=forms.TextInput(attrs={'type': "text", 'id': "first_name", 'class': "form-control", 'placeholder': "First name"}))
    last_name = forms.CharField(label=False, max_length=30, required=True, widget=forms.TextInput(attrs={'type': "text", 'id': "last_name", 'class': "form-control", 'placeholder': "Last name"}))
    dob = forms.DateField(label=False, required=True, widget=forms.DateInput(attrs={'type': "date", 'class': "form-control", 'id': "dob", 'placeholder': "2020-02-20", 'max':"9999-12-31"}))
    email1 = forms.EmailField(label=False, max_length=254, required=True, widget=forms.TextInput(attrs={'class': 'form-control email-inputs', 'maxlength': '50', 'placeholder': 'Email', 'id':'email1', 'aria-describedby': 'email-match-help'}))
    email2 = forms.EmailField(label=False, max_length=254, required=True, widget=forms.TextInput(attrs={'class': 'form-control email-inputs', 'maxlength': '50', 'placeholder': 'Confirm Email', 'id':'email2'}))
    password1 = forms.CharField(label=False, widget=forms.PasswordInput(attrs={'class': 'form-control pass-inputs', 'placeholder': 'Password', 'id':'password1', 'aria-describedby': 'password-match-help'}), required=True)
    password2 = forms.CharField(label=False, widget=forms.PasswordInput(attrs={'class': 'form-control pass-inputs', 'placeholder': 'Confirm Password', 'id':'password2'}), required=True)
    phone1 = forms.IntegerField(label=False, required=True, widget=forms.NumberInput(attrs={'type': "number", 'min':'0', 'onkeypress':"return event.charCode >= 48", 'class': "form-control phone-inputs", 'id': "phone1", 'maxlength': "3", 'placeholder': "XXX"}))
    phone2 = forms.IntegerField(label=False, required=True, widget=forms.NumberInput(attrs={'type': "number", 'min':'0', 'onkeypress':"return event.charCode >= 48", 'class': "form-control phone-inputs", 'id': "phone2", 'maxlength': "3", 'placeholder': "XXX"}))
    phone3 = forms.IntegerField(label=False, required=True, widget=forms.NumberInput(attrs={'type': "number", 'min':'0', 'onkeypress':"return event.charCode >= 48", 'class': "form-control phone-inputs", 'id': "phone3", 'maxlength': "4", 'placeholder': "XXXX"}))
    ohip1 = forms.IntegerField(label=False, required=True, widget=forms.NumberInput(attrs={'type': "number", 'min':'0', 'onkeypress':"return event.charCode >= 48", 'class': "form-control ohip-inputs", 'id': "ohip1", 'maxlength': "4", 'placeholder': "XXXX"}))
    ohip2 = forms.IntegerField(label=False, required=True, widget=forms.NumberInput(attrs={'type': "number", 'min':'0', 'onkeypress':"return event.charCode >= 48", 'class': "form-control ohip-inputs", 'id': "ohip2", 'maxlength': "3", 'placeholder': "XXX"}))
    ohip3 = forms.IntegerField(label=False, required=True, widget=forms.NumberInput(attrs={'type': "number", 'min':'0', 'onkeypress':"return event.charCode >= 48", 'class': "form-control ohip-inputs", 'id': "ohip3", 'maxlength': "3", 'placeholder': "XXX"}))
    ohip_version = forms.CharField(label=False, max_length=2, required=True, widget=forms.TextInput(attrs={'type':"text", 'class':"form-control ohip-inputs", 'id':"ohip-version", 'maxlength':"2", 'placeholder':"XX", 'style':'text-transform: uppercase',}))
    ohip_expiry = forms.DateField(label=False, required=True, widget=forms.DateInput(attrs={'type': "date", 'class': "form-control", 'id': "ohip-expiry", 'placeholder': "2020-02-20", 'max':"9999-12-31"}))

class DoctorEditForm(forms.Form):
    first_name = forms.CharField(label=False, max_length=30, required=True, widget=forms.TextInput(attrs={'type': "text", 'id': "first_name", 'class': "form-control", 'placeholder': "First name"}))
    last_name = forms.CharField(label=False, max_length=30, required=True, widget=forms.TextInput(attrs={'type': "text", 'id': "last_name", 'class': "form-control", 'placeholder': "Last name"}))
    dob = forms.DateField(label=False, required=True, widget=forms.DateInput(attrs={'type': "date", 'class': "form-control", 'id': "dob", 'max':"9999-12-31"}))
    phone1 = forms.IntegerField(label=False, required=True, widget=forms.NumberInput(attrs={'type': "number", 'min':'0', 'onkeypress':"return event.charCode >= 48", 'class': "form-control phone-inputs", 'id': "phone1", 'maxlength': "3", 'placeholder': "XXX"}))
    phone2 = forms.IntegerField(label=False, required=True, widget=forms.NumberInput(attrs={'type': "number", 'min':'0', 'onkeypress':"return event.charCode >= 48", 'class': "form-control phone-inputs", 'id': "phone2", 'maxlength': "3", 'placeholder': "XXX"}))
    phone3 = forms.IntegerField(label=False, required=True, widget=forms.NumberInput(attrs={'type': "number", 'min':'0', 'onkeypress':"return event.charCode >= 48", 'class': "form-control phone-inputs", 'id': "phone3", 'maxlength': "4", 'placeholder': "XXXX"}))
    qualifications = forms.CharField(label=False, widget=forms.Textarea())
    consultations = forms.CharField(label=False, widget=forms.HiddenInput())
    languages = forms.CharField(label=False, widget=forms.HiddenInput())

class PatientEditForm(forms.Form):
    first_name = forms.CharField(label=False, max_length=30, required=True, widget=forms.TextInput(attrs={'type': "text", 'id': "first_name", 'class': "form-control", 'placeholder': "First name"}))
    last_name = forms.CharField(label=False, max_length=30, required=True, widget=forms.TextInput(attrs={'type': "text", 'id': "last_name", 'class': "form-control", 'placeholder': "Last name"}))
    dob = forms.DateField(label=False, required=True, widget=forms.DateInput(attrs={'type': "date", 'class': "form-control", 'id': "dob", 'max':"9999-12-31"}))
    phone1 = forms.IntegerField(label=False, required=True, widget=forms.NumberInput(attrs={'type': "number", 'min':'0', 'onkeypress':"return event.charCode >= 48", 'class': "form-control phone-inputs", 'id': "phone1", 'maxlength': "3", 'placeholder': "XXX"}))
    phone2 = forms.IntegerField(label=False, required=True, widget=forms.NumberInput(attrs={'type': "number", 'min':'0', 'onkeypress':"return event.charCode >= 48", 'class': "form-control phone-inputs", 'id': "phone2", 'maxlength': "3", 'placeholder': "XXX"}))
    phone3 = forms.IntegerField(label=False, required=True, widget=forms.NumberInput(attrs={'type': "number", 'min':'0', 'onkeypress':"return event.charCode >= 48", 'class': "form-control phone-inputs", 'id': "phone3", 'maxlength': "4", 'placeholder': "XXXX"}))
    ohip1 = forms.IntegerField(label=False, required=True, widget=forms.NumberInput(attrs={'type': "number", 'min':'0', 'onkeypress':"return event.charCode >= 48", 'class': "form-control ohip-inputs", 'id': "ohip1", 'maxlength': "4", 'placeholder': "XXXX"}))
    ohip2 = forms.IntegerField(label=False, required=True, widget=forms.NumberInput(attrs={'type': "number", 'min':'0', 'onkeypress':"return event.charCode >= 48", 'class': "form-control ohip-inputs", 'id': "ohip2", 'maxlength': "3", 'placeholder': "XXX"}))
    ohip3 = forms.IntegerField(label=False, required=True, widget=forms.NumberInput(attrs={'type': "number", 'min':'0', 'onkeypress':"return event.charCode >= 48", 'class': "form-control ohip-inputs", 'id': "ohip3", 'maxlength': "3", 'placeholder': "XXX"}))
    ohip_version = forms.CharField(label=False, max_length=2, required=True, widget=forms.TextInput(attrs={'type':"text", 'class':"form-control ohip-inputs", 'id':"ohip-version", 'maxlength':"2", 'placeholder':"XX", 'style':'text-transform: uppercase',}))
    ohip_expiry = forms.DateField(label=False, required=True, widget=forms.DateInput(attrs={'type': "date", 'class': "form-control", 'id': "ohip-expiry", 'max':"9999-12-31"}))
