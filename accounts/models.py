from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.utils.translation import gettext_lazy as _
from django.urls import reverse
from django.core.validators import RegexValidator, EmailValidator, MinValueValidator, MaxValueValidator
from django.utils import timezone
from datetime import datetime
from pytz import utc

# Create your models here.

class CustomUserManager(BaseUserManager):
    """
    Custom user model manager where email is the unique identifiers
    for authentication instead of usernames.
    """
    def create_user(self, email, password, **extra_fields):
        """
        Create and save a User with the given email and password.
        """
        if not email:
            raise ValueError(_('The Email must be set'))
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save()
        return user

    def create_superuser(self, email, password, **extra_fields):
        """
        Create and save a SuperUser with the given email and password.
        """
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError(_('Superuser must have is_staff=True.'))
        if extra_fields.get('is_superuser') is not True:
            raise ValueError(_('Superuser must have is_superuser=True.'))
        return self.create_user(email, password, **extra_fields)


class User(AbstractUser):

    class Types(models.TextChoices):
        PATIENT = "PATIENT", "Patient"
        DOCTOR = "DOCTOR", "Doctor"
        #ADMIN = "ADMIN", "Admin"

    type = models.CharField(_('Type'), max_length=50, choices=Types.choices)
    username = None
    phone = models.CharField(_("User Phone Number"), max_length=10, blank=True, null=True,validators=[RegexValidator(regex='^.{10}$', message="Phone number must be 10 digits long", code='nomatch')])
    first_name = models.CharField(_("User First Name"), max_length=50)
    preferred_name = models.CharField(_("User Preferred Name"), max_length=50, blank=True, null=True, default=None)
    last_name = models.CharField(_("User Last Name"), max_length=50)
    email = models.EmailField(_("User Email"), validators=[EmailValidator("Please enter a valid e-mail")], max_length=50, unique=True)
    target_new_email = models.EmailField(_("Possible New Email"), max_length=50, unique=True, blank=True, null=True, default=None)
    ms_authenticated = models.BooleanField(_("Connected to MS Account"), default=False)
    email_notifications = models.BooleanField(_("Email Notifications"), default=True)
    sms_notifications = models.BooleanField(_("SMS Notifications"), default=True)
    
    USERNAME_FIELD='email'
    REQUIRED_FIELDS = []

    objects = CustomUserManager()

    def __str__(self):
        return f'{str(self.first_name)} {str(self.last_name)}'

    def get_absolute_url(self):
        return reverse("users:detail", kwargs={"username": self.username})

    # Returns the proxy model object associated to the User
    @property
    def userType(self):
        if (self.type == 'DOCTOR'):
            return Doctor.objects.get(pk=self.pk)
        elif (self.type == 'PATIENT'):
            return Patient.objects.get(pk=self.pk)

    # Returns the Queryset of all Appointment objects that are scheduled to the User
    @property
    def getAppts(self):
        from book.models import Appointment
        if (self.type == 'PATIENT'):
            return Appointment.objects.filter(patient=self, datetime__gt = datetime.now().astimezone(utc)).order_by('date', 'time')
        elif (self.type == 'DOCTOR'):
            return Appointment.objects.filter(doctor=self, datetime__gt = datetime.now().astimezone(utc)).order_by('date', 'time')
    
    # Limits getAppts to the first 10 Appointment objects
    @property
    def getSomeAppts(self):
        return self.getAppts[:10]

    @property
    def formattedPhone(self):
        return '(' + self.phone[:3] + ') ' + self.phone[3:6] + '-' + self.phone[6:10]

# Allows for querying within the Patient object
class PatientManager(CustomUserManager):
    def get_queryset(self, *args, **kwargs):
        return super().get_queryset(*args, **kwargs).filter(type=User.Types.PATIENT)

# Allows for querying within the Doctor object
class DoctorManager(CustomUserManager):
    def get_queryset(self, *args, **kwargs):
        return super().get_queryset(*args, **kwargs).filter(type=User.Types.DOCTOR)

class Patient(User):
    objects = PatientManager()
    @property
    def more(self):
        return self.patientinfo

    class Meta:
        proxy = True

# Details for Patient object, linked one-to-one
class PatientInfo(models.Model):
    user = models.OneToOneField(Patient, on_delete=models.CASCADE, unique=True)
    dob = models.DateField(default=timezone.now)
    ohip_number = models.CharField(_("OHIP Number"), max_length=15, unique=True, validators=[RegexValidator(regex='^.{15}$', message="Must be in format XXXX-XXX-XXX-XX", code='nomatch')])
    #ohip_version_code = models.CharField(_("OHIP Version Code"), max_length=2, validators=[RegexValidator(regex='^{2}$', message="Length must be 2", code='nomatch')])
    ohip_expiry = models.DateField(_("OHIP Expiry Date"), default=timezone.now)
    address = models.CharField(_("User Address"), null=True, blank=True, max_length=100, default=None)
    postal_code = models.CharField(_("User Postal Code"), null=True, blank=True, max_length=7, default=None)
    address_coords = models.CharField(_("User Address (lat,long)"), null=True, blank=True, max_length=50, default=None)
    pharmacy = models.CharField(_("User Preferred Pharmacy"), max_length=250, null=True, blank=True, default=None)


class Doctor(User):
    objects = DoctorManager()
    @property
    def more(self):
        return self.doctorinfo
    
    class Meta:
        proxy = True
    
    @property
    def getSomeBookedAppts(self):
        return self.getAppts.filter(booked=True)[:10]

    @property
    def getSomeOpenAppts(self):
        return self.getAppts.filter(booked=False)[:10]

    @property
    def upcomingGroups(self):
        return [{'name':'all', 'appts':self.getSomeAppts}, {'name':'open', 'appts':self.getSomeOpenAppts}, {'name':'booked', 'appts':self.getSomeBookedAppts}]

    @property
    def apptGroupLengths(self):
        return {
            'all': len(self.getAppts),
            'open': len(self.getAppts.filter(booked=False)),
            'booked': len(self.getAppts.filter(booked=True)),
        }

# Details for Doctor object, linked one-to-one
class DoctorInfo(models.Model):
    user = models.OneToOneField(Doctor, on_delete=models.CASCADE, unique=True)
    certification = models.CharField(_("Doctor Qualifications"), max_length=50, default="None")
    consultations = models.TextField(_("Doctor's Applicable Consultations"))
    languages = models.CharField(_("Doctor's Known Languages"), max_length=100, default="None")
    location = models.CharField(_("Office Location"), null=True, blank=True, max_length=100, default=None)

# Function that can be run in Python shell to create a Doctor object and its corresponding DoctorInfo (temporary)
def createdoctor():
    first_name = input("Enter first name: ")
    last_name = input("Enter last name: ")
    email = input("Enter email: ")
    password = input("Enter password: ")
    phone = input("Enter phone number: ")
    certification = input("Enter certifications: ")
    consultations = input("Enter consultations: ")
    languages = input("Enter languages: ")

    d = User.objects.create(first_name=first_name, password=password, last_name=last_name, email=email, phone=phone, type=User.Types.DOCTOR)
    d.set_password(password)
    d.save()
    DoctorInfo.objects.create(user=d, certification=certification, consultations=consultations, languages=languages)
    print("Doctor created!")