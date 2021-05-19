from django.contrib import admin
from .models import User, Patient, Doctor, PatientInfo, DoctorInfo

# Register your models here.
admin.site.register(User)
admin.site.register(Doctor)
admin.site.register(Patient)
admin.site.register(PatientInfo)
admin.site.register(DoctorInfo)