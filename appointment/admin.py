from django.contrib import admin
from .models import ApptDetails, ApptFile

# Register your models here.

admin.site.register(ApptDetails)
admin.site.register(ApptFile)