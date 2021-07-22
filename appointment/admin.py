from django.contrib import admin
from .models import ApptDetails, ApptImage

# Register your models here.

admin.site.register(ApptDetails)
admin.site.register(ApptImage)