from django import forms
from .models import User


class SignUpForm(forms.Form):
    first_name = forms.CharField(label=False, max_length=30, required=True, widget=forms.TextInput(attrs={'type': "text", 'id': "first_name", 'class': "formcontrol", 'placeholder': "First name*"}))
    preferred_name = forms.CharField(label=False, max_length=30, required=False, widget=forms.TextInput(attrs={'type': "text", 'id': "preferred_name", 'class': "formcontrol", 'placeholder': "Preferred name"}))
    last_name = forms.CharField(label=False, max_length=30, required=True, widget=forms.TextInput(attrs={'type': "text", 'id': "last_name", 'class': "formcontrol", 'placeholder': "Last name*"}))
    email1 = forms.EmailField(label=False, max_length=254, required=True, widget=forms.TextInput(attrs={'class': 'formcontrol email-inputs', 'maxlength': '50', 'placeholder': 'Email*', 'id':'email1', 'aria-describedby': 'email-match-help'}))
    email2 = forms.EmailField(label=False, max_length=254, required=True, widget=forms.TextInput(attrs={'class': 'formcontrol email-inputs', 'maxlength': '50', 'placeholder': 'Confirm Email*', 'id':'email2'}))
    password1 = forms.CharField(label=False, widget=forms.PasswordInput(attrs={'class': 'formcontrol pass-inputs', 'placeholder': 'Password*', 'id':'password1', 'aria-describedby': 'password-match-help'}), required=True)
    password2 = forms.CharField(label=False, widget=forms.PasswordInput(attrs={'class': 'formcontrol pass-inputs', 'placeholder': 'Confirm Password*', 'id':'password2'}), required=True)
    phone = forms.CharField(label=False, required=False, max_length=15, widget=forms.TextInput(attrs={'type': "text", 'class': "formcontrol phone-input", 'id': "phone", 'placeholder':"Phone Number", 'autocomplete':'password', 'onkeypress':"if (this.value.length < 14) {return (event.charCode >= 48 && event.charCode <= 57)} else {return false}"}))
    address = forms.CharField(label=False, required=False, widget=forms.TextInput(attrs={'type': "text", 'id': "address", 'class': "formcontrol", 'placeholder': "Address"}))
    # ohip_version = forms.CharField(label=False, max_length=2, required=True, widget=forms.TextInput(attrs={'type':"text", 'class':"formcontrol ohip-inputs", 'onkeypress':"if (this.value.length < 2) {return (event.charCode >= 65 && event.charCode <= 90) || (event.charCode >= 97 && event.charCode <= 122)} else {return false}", 'id':"ohip-version", 'maxlength':"2", 'placeholder':"OHIP Version*", 'style':'text-transform: uppercase'}))
    
class PatientSignUpForm(SignUpForm):
    dob = forms.DateField(label=False, required=True, widget=forms.DateInput(attrs={'type': "text", 'class': "formcontrol", 'id': "dob", 'placeholder': "Date of Birth*", "onfocus": "(this.type='date')", "onblur": "(this.value ? this.type='date' : this.type='text')", 'max':"9999-12-31"}))
    postal_code = forms.CharField(label=False, required=False, widget=forms.TextInput(attrs={'type': "text", 'id': "postal_code", 'class': "formcontrol", 'placeholder': "Postal Code"}))
    ohip = forms.CharField(label=False, required=True, max_length=15, widget=forms.TextInput(attrs={'type': "text", 'class': "formcontrol ohip-inputs", 'id': "ohip", 'placeholder':"OHIP Number", 'onkeypress':"if (this.value.length < 12) {return (event.charCode >= 48 && event.charCode <= 57)} else {return ((event.charCode >= 65 && event.charCode <= 90) || (event.charCode >= 97 && event.charCode <= 122)) && this.value.length < 15}", 'style':'text-transform: uppercase'}))
    ohip_expiry = forms.DateField(label=False, required=True, widget=forms.DateInput(attrs={'type': "text", 'class': "formcontrol", 'id': "ohip-expiry", 'placeholder': "OHIP Expiry Date*", "onfocus": "(this.type='date')", "onblur": "(this.value ? this.type='date' : this.type='text')", 'max':"9999-12-31"}))


class UserEditForm(forms.Form):
    first_name = forms.CharField(label=False, max_length=30, required=True, widget=forms.TextInput(attrs={'type': "text", 'id': "first_name", 'class': "formcontrol", 'placeholder': "First name"}))
    preferred_name = forms.CharField(label=False, max_length=30, required=False, widget=forms.TextInput(attrs={'type': "text", 'id': "preferred_name", 'class': "formcontrol", 'placeholder': "Preferred name"}))
    last_name = forms.CharField(label=False, max_length=30, required=True, widget=forms.TextInput(attrs={'type': "text", 'id': "last_name", 'class': "formcontrol", 'placeholder': "Last name"}))
    email = forms.CharField(label=False, required=True, max_length=50, widget=forms.TextInput(attrs={'type': "email", 'class': "formcontrol", 'id': "email", 'placeholder':"Email", 'autocomplete':'password'}))
    init_email = forms.CharField(label=False, required=True, widget=forms.HiddenInput())
    #phone = forms.IntegerField(label=False, required=False, widget=forms.NumberInput(attrs={'type': "number", 'min':'0', 'onkeypress':"if (this.value.length < 10) {return event.charCode >= 48} else {return false}", 'class': "formcontrol", 'id': "phone", 'max': "9999999999", 'placeholder': "Phone Number*", "autocomplete":"new-password"}))
    phone = forms.CharField(label=False, required=False, max_length=15, widget=forms.TextInput(attrs={'type': "text", 'class': "formcontrol phone-input", 'id': "phone", 'placeholder':"Phone Number", 'autocomplete':'password', 'onkeypress':"if (this.value.length < 14) {return (event.charCode >= 48 && event.charCode <= 57)} else {return false}"}))
    # phone1 = forms.IntegerField(label=False, required=True, widget=forms.NumberInput(attrs={'type': "number", 'min':'0', 'onkeypress':"return event.charCode >= 48", 'class': "formcontrol phone-inputs", 'id': "phone1", 'maxlength': "3", 'placeholder': "XXX"}))
    # phone2 = forms.IntegerField(label=False, required=True, widget=forms.NumberInput(attrs={'type': "number", 'min':'0', 'onkeypress':"return event.charCode >= 48", 'class': "formcontrol phone-inputs", 'id': "phone2", 'maxlength': "3", 'placeholder': "XXX"}))
    # phone3 = forms.IntegerField(label=False, required=True, widget=forms.NumberInput(attrs={'type': "number", 'min':'0', 'onkeypress':"return event.charCode >= 48", 'class': "formcontrol phone-inputs", 'id': "phone3", 'maxlength': "4", 'placeholder': "XXXX"}))
    email_notis = forms.BooleanField(label=False, required=False, widget=forms.CheckboxInput(attrs={'data-toggle':'toggle', 'data-on': 'On', 'data-off': 'Off', 'data-onstyle':'success', 'data-offstyle':'secondary', 'class':'email-notis'}))
    sms_notis = forms.BooleanField(label=False, required=False, widget=forms.CheckboxInput(attrs={'data-toggle':'toggle', 'data-on': 'On', 'data-off': 'Off', 'data-onstyle':'success', 'data-offstyle':'secondary', 'class':'sms-notis'}))

class DoctorEditForm(UserEditForm):
    qualifications = forms.CharField(label=False, required=True, widget=forms.Textarea(attrs={'class':'formcontrol'}))
    consultations = forms.CharField(label=False, required=False, widget=forms.HiddenInput())
    languages = forms.CharField(label=False, required=False, widget=forms.HiddenInput())
    location = forms.CharField(label=False, required=False, widget=forms.TextInput(attrs={'type': "text", 'placeholder':'Location', 'class':'formcontrol'}))
    

class PatientEditForm(UserEditForm):
    dob = forms.DateField(label=False, required=True, widget=forms.DateInput(attrs={'type': "date", 'class': "formcontrol", 'id': "dob", 'max':"9999-12-31"}))
    address = forms.CharField(label=False, required=True, widget=forms.TextInput(attrs={'type': "text", 'id': "address", 'class': "formcontrol", 'placeholder': "Address"}))
    postal_code = forms.CharField(label=False, required=True, widget=forms.TextInput(attrs={'type': "text", 'id': "postal_code", 'class': "formcontrol", 'placeholder': "Postal Code"}))
    # ohip1 = forms.IntegerField(label=False, required=True, widget=forms.NumberInput(attrs={'type': "number", 'min':'0', 'onkeypress':"return event.charCode >= 48", 'class': "formcontrol ohip-inputs", 'id': "ohip1", 'maxlength': "4", 'placeholder': "XXXX"}))
    # ohip2 = forms.IntegerField(label=False, required=True, widget=forms.NumberInput(attrs={'type': "number", 'min':'0', 'onkeypress':"return event.charCode >= 48", 'class': "formcontrol ohip-inputs", 'id': "ohip2", 'maxlength': "3", 'placeholder': "XXX"}))
    # ohip3 = forms.IntegerField(label=False, required=True, widget=forms.NumberInput(attrs={'type': "number", 'min':'0', 'onkeypress':"return event.charCode >= 48", 'class': "formcontrol ohip-inputs", 'id': "ohip3", 'maxlength': "3", 'placeholder': "XXX"}))
    # ohip_version = forms.CharField(label=False, max_length=2, required=True, widget=forms.TextInput(attrs={'type':"text", 'class':"formcontrol ohip-inputs", 'id':"ohip-version", 'maxlength':"2", 'placeholder':"XX", 'style':'text-transform: uppercase',}))
    ohip = forms.CharField(label=False, required=True, max_length=15, widget=forms.TextInput(attrs={'type': "text", 'class': "formcontrol ohip-inputs", 'id': "ohip", 'placeholder':"OHIP Number", 'onkeypress':"if (this.value.length < 12) {return (event.charCode >= 48 && event.charCode <= 57)} else {return ((event.charCode >= 65 && event.charCode <= 90) || (event.charCode >= 97 && event.charCode <= 122)) && this.value.length < 15}", 'style':'text-transform: uppercase'}))
    ohip_expiry = forms.DateField(label=False, required=True, widget=forms.DateInput(attrs={'type': "date", 'class': "formcontrol", 'id': "ohip-expiry", 'max':"9999-12-31"}))
    