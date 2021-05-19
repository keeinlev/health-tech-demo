from django import forms
from .models import Prescription

class PrescriptionForm(forms.ModelForm):
    prescription = forms.CharField(required=False, widget=forms.Textarea(attrs={'class': 'form-control pass-inputs', 'placeholder':"Patient Prescription"}))
    notes = forms.CharField(required=False, widget=forms.Textarea(attrs={'class': 'form-control pass-inputs', 'placeholder':"Patient Notes"}))
    track_number = forms.CharField(required=False, widget=forms.TextInput(attrs={'class': 'form-control pass-inputs', 'placeholder':"Tracking Number"}))
    class Meta:
        model=Prescription
        fields=['prescription', 'notes', 'track_number']