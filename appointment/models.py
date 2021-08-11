from django.db import models
from django.utils.translation import gettext_lazy as _
from book.models import Appointment
import uuid
from django.utils.timezone import now as todayDate
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from django.db.models.signals import pre_delete
from django.conf import settings

def get_upload_path(instance, filename):
    fileType = filename[filename.index('.'):]
    return f'{urlsafe_base64_encode(force_bytes(instance.appt.doctor.pk))}/{urlsafe_base64_encode(force_bytes(instance.appt.patient.pk))}/{urlsafe_base64_encode(force_bytes(instance.appt.pk))}/{instance.unique_id}{fileType}'

# Create your models here.
class ApptDetails(models.Model):
    date = models.DateField(default=None, null=True)
    appt = models.OneToOneField(Appointment, on_delete=models.CASCADE, default=None)
    prescription = models.CharField(_("Prescription"), max_length=50, default='', null=True)
    notes = models.CharField(_("Additional Notes"), max_length=50, default='', null=True)

def delete_apptfile(sender, instance, using, **kwargs):
    if settings.DEFAULT_FILE_STORAGE == 'storages.backends.azure_storage.AzureStorage':
        blob_name = instance.get_blob_url
        blob_service = settings.BLOB_SERVICE
        try:
            blob_service.delete_blob(container_name=settings.AZURE_CONTAINER, blob_name=blob_name)
        except AzureMissingResourceHttpError as e:
            print('This blob does not exist or has already been deleted. Error: ' + str(e)[str(e).index('<Message>') + len('<Message>'):str(e).index('</Message>')])

class ApptFile(models.Model):
    unique_id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    upload_date = models.DateField(default=todayDate)
    appt = models.ForeignKey(Appointment(), related_name="%(class)s_appt", on_delete=models.CASCADE, null=True, default=None)
    uploaded_file = models.FileField(upload_to=get_upload_path)
    file_type = models.CharField(_("File Extension Type"), max_length=10, default='', null=True)
    content_type = models.CharField(_("File Content Type"), max_length=71, default='', null=True)
    friendly_name = models.CharField(_("Original Uploaded Name"), max_length=100, default='', null=True)
    
    @property
    def get_blob_url(self):
        from django.conf import settings
        url = self.uploaded_file.url
        url = url[url.index(settings.AZURE_CONTAINER) + len(settings.AZURE_CONTAINER) + 1:]
        return url[:url.index(self.file_type) + len(self.file_type)]

    @property
    def isMedia(self):
        return self in self.appt.getMedia
    
pre_delete.connect(delete_apptfile, sender=ApptFile)