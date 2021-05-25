from django.contrib import admin
from .models import User, Patient, Doctor, PatientInfo, DoctorInfo

from django import forms
from django.contrib import admin
from django.contrib.auth.models import Group
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

class UserAdmin(BaseUserAdmin):
    list_display = ('email', 'first_name', 'last_name', 'dob', 'type', 'is_active', 'is_superuser', 'id')
    fieldsets = (
        (None, {'fields': ('email', 'password', 'type', 'is_active')}),
        ('Personal info', {'fields': ('first_name', 'last_name', 'phone', 'dob',)}),
    )
    # add_fieldsets is not a standard ModelAdmin attribute. UserAdmin
    # overrides get_fieldsets to use this attribute when creating a user.
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'dob', 'password1', 'password2')}
        ),
        ('Personal info', {'fields': ('first_name', 'last_name', 'phone', 'dob',)})
    )
    search_fields = ('email',)
    ordering = ('email',)
    filter_horizontal = ()

# Register your models here.
admin.site.register(User, UserAdmin)
admin.site.unregister(Group)
admin.site.register(Doctor, UserAdmin)
admin.site.register(Patient, UserAdmin)
admin.site.register(PatientInfo)
admin.site.register(DoctorInfo)