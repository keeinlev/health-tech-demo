from django.db import models
from django.utils.translation import gettext_lazy as _
from book.models import Appointment
import uuid
from django.utils.timezone import now as todayDate
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode

def get_upload_path(instance, filename):
    fileType = filename[filename.index('.'):]
    return f'{urlsafe_base64_encode(force_bytes(instance.appt.doctor.pk))}/{urlsafe_base64_encode(force_bytes(instance.appt.patient.pk))}/{urlsafe_base64_encode(force_bytes(instance.appt.pk))}/{instance.unique_id}{fileType}'

# Create your models here.
class ApptDetails(models.Model):
    date = models.DateField(default=None, null=True)
    appt = models.OneToOneField(Appointment, on_delete=models.CASCADE, default=None)
    prescription = models.CharField(_("Prescription"), max_length=50, default='', null=True)
    notes = models.CharField(_("Additional Notes"), max_length=50, default='', null=True)

class ApptFile(models.Model):
    unique_id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    upload_date = models.DateField(default=todayDate)
    appt = models.ForeignKey(Appointment(), related_name="%(class)s_appt", on_delete=models.CASCADE, null=True, default=None)
    uploaded_file = models.FileField(upload_to=get_upload_path)
    file_type = models.CharField(_("File Extension Type"), max_length=10, default='', null=True)
    content_type = models.CharField(_("File Content Type"), max_length=50, default='', null=True)
    friendly_name = models.CharField(_("Original Uploaded Name"), max_length=100, default='', null=True)
    
    @property
    def get_blob_url(self):
        from django.conf import settings
        url = self.image.url
        url = url[url.index(settings.AZURE_CONTAINER) + len(settings.AZURE_CONTAINER) + 1:]
        return url[:url.index('.png') + len('.png')]

    @property
    def isMedia(self):
        return self in self.appt.getMedia
    