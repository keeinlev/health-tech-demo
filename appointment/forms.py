from django import forms
from .models import ApptDetails

class ApptDetailsForm(forms.ModelForm):
    prescription = forms.CharField(required=False, widget=forms.Textarea(attrs={'class': 'form-control pass-inputs', 'placeholder':"Patient Prescription"}))
    notes = forms.CharField(required=False, widget=forms.Textarea(attrs={'class': 'form-control pass-inputs', 'placeholder':"Patient Notes"}))
    class Meta:
        model=ApptDetails
        fields=['prescription', 'notes']