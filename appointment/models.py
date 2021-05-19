from django.db import models
from django.utils.translation import gettext_lazy as _
from book.models import Appointment

# Create your models here.
class Prescription(models.Model):
    date = models.DateField(default=None, null=True)
    appt = models.OneToOneField(Appointment, on_delete=models.CASCADE, default=None)
    prescription = models.CharField(_("Prescription"), max_length=50, default='', null=True)
    track_number = models.CharField(_("Tracking Number"), max_length=50, default='', null=True)
    notes = models.CharField(_("Additional Notes"), max_length=50, default='', null=True)