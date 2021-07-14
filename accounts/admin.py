from django.contrib import admin
from .models import User, Patient, Doctor, PatientInfo, DoctorInfo

from django import forms
from django.contrib import admin
from django.contrib.auth.models import Group
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin


# This class handles what gets shown on the User Model page in the Django Admin site
# This is required for the Custom User model since it inherits from the BaseUser, which will give its own set of fields to the Admin page,
#   some of which do not align with our requirements
class UserAdmin(BaseUserAdmin):

    # Change what fields are displayed when viewing existing Users
    list_display = ('email', 'first_name', 'last_name', 'type', 'is_active', 'is_superuser', 'id')

    # Change what fields are accepted in User editing
    fieldsets = (
        (None, {'fields': ('email', 'password', 'type', 'is_active')}),
        ('Personal info', {'fields': ('first_name', 'preferred_name', 'last_name', 'phone',)}),
    )

    # Change what fields are accepted in User creation
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('type', 'email', 'password1', 'password2')}
        ),
        ('Personal info', {'fields': ('first_name', 'preferred_name', 'last_name', 'phone',)})
    )
    
    # What field to search by
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