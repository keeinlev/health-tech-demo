from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.utils.translation import gettext_lazy as _
from django.urls import reverse
from django.core.validators import RegexValidator, validate_email, EmailValidator, MinValueValidator, MaxValueValidator
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
    phone = models.CharField(_("User Phone Number"), max_length=10, validators=[RegexValidator(regex='^.{10}$', message="Phone number must be 10 digits long", code='nomatch')])
    first_name = models.CharField(_("User First Name"), max_length=50)
    preferred_name = models.CharField(_("User Preferred Name"), max_length=50, blank=True, null=True, default=None)
    last_name = models.CharField(_("User Last Name"), max_length=50)
    email = models.EmailField(_("User Email"), validators=[EmailValidator("Please enter a valid e-mail")], max_length=50, unique=True)
    dob = models.DateField(default=timezone.now)
    ms_authenticated = models.BooleanField(_("Connected to MS Account"), default=False)
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    objects = CustomUserManager()

    def __str__(self):
        return f'{str(self.first_name)} {str(self.last_name)}'

    def get_absolute_url(self):
        return reverse("users:detail", kwargs={"username": self.username})

    @property
    def userType(self):
        if (self.type == 'DOCTOR'):
            return Doctor.objects.get(pk=self.pk)
        elif (self.type == 'PATIENT'):
            return Patient.objects.get(pk=self.pk)

    @property
    def getAppts(self):
        from book.models import Appointment
        if (self.type == 'PATIENT'):
            return Appointment.objects.filter(patient=self, datetime__gt = datetime.now().astimezone(utc)).order_by('date', 'time')
        elif (self.type == 'DOCTOR'):
            return Appointment.objects.filter(doctor=self, datetime__gt = datetime.now().astimezone(utc)).order_by('date', 'time')
    
    @property
    def getSomeAppts(self):
        from book.models import Appointment
        if (self.type == 'PATIENT'):
            return Appointment.objects.filter(patient=self, datetime__gt = datetime.now().astimezone(utc)).order_by('date', 'time')[:10]
        elif (self.type == 'DOCTOR'):
            return Appointment.objects.filter(doctor=self, datetime__gt = datetime.now().astimezone(utc)).order_by('date', 'time')[:10]

class PatientManager(CustomUserManager):
    def get_queryset(self, *args, **kwargs):
        return super().get_queryset(*args, **kwargs).filter(type=User.Types.PATIENT)

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

class PatientInfo(models.Model):
    user = models.OneToOneField(Patient, on_delete=models.CASCADE, unique=True)
    ohip_number = models.CharField(_("OHIP Number"), max_length=15, unique=True, validators=[RegexValidator(regex='^.{15}$', message="Must be in format XXXX-XXX-XXX-XX", code='nomatch')])
    #ohip_version_code = models.CharField(_("OHIP Version Code"), max_length=2, validators=[RegexValidator(regex='^{2}$', message="Length must be 2", code='nomatch')])
    ohip_expiry = models.DateField(_("OHIP Expiry Date"), default=timezone.now)


class Doctor(User):
    objects = DoctorManager()

    @property
    def more(self):
        return self.doctorinfo
    
    class Meta:
        proxy = True


class DoctorInfo(models.Model):
    user = models.OneToOneField(Doctor, on_delete=models.CASCADE, unique=True)
    certification = models.CharField(_("Doctor Qualifications"), max_length=50, default="None")
    consultations = models.TextField(_("Doctor's Applicable Consultations"))
    languages = models.CharField(_("Doctor's Known Languages"), max_length=100, default="None")

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
    print("Doctor created! Please add a meeting URL in the Edit Profile page once logged in.")