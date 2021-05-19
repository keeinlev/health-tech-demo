from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.utils.translation import gettext_lazy as _
from django.urls import reverse
from django.core.validators import RegexValidator, validate_email, EmailValidator, MinValueValidator, MaxValueValidator
from django.utils import timezone

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
    phone = models.CharField(_("User Phone Number"), max_length=14, validators=[RegexValidator(regex='^{14}$', message="Length must be 14", code='nomatch')])
    first_name = models.CharField(_("User First Name"), max_length=50)
    last_name = models.CharField(_("User Last Name"), max_length=50)
    email = models.EmailField(_("User Email"), validators=[EmailValidator("Please enter a valid e-mail")], max_length=50, unique=True)
    dob = models.DateField(default=timezone.now)
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    objects = CustomUserManager()

    def __str__(self):
        return f'{str(self.first_name)} {str(self.last_name)}'

    def get_absolute_url(self):
        return reverse("users:detail", kwargs={"username": self.username})


class PatientManager(models.Manager):
    def get_queryset(self, *args, **kwargs):
        return super().get_queryset(*args, **kwargs).filter(type=User.Types.PATIENT)

class DoctorManager(models.Manager):
    def get_queryset(self, *args, **kwargs):
        return super().get_queryset(*args, **kwargs).filter(type=User.Types.DOCTOR)


class PatientInfo(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    ohip_number = models.CharField(_("OHIP Number"), max_length=15, unique=True, validators=[RegexValidator(regex='^{15}$', message="Length must be 15", code='nomatch')])
    #ohip_version_code = models.CharField(_("OHIP Version Code"), max_length=2, validators=[RegexValidator(regex='^{2}$', message="Length must be 2", code='nomatch')])
    ohip_expiry = models.DateField(_("OHIP Expiry Date"), default=timezone.now)

class Patient(User):
    objects = PatientManager()

    @property
    def more(self):
        return self.patientinfo

    class Meta:
        proxy = True


class DoctorInfo(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    certification = models.CharField(_("Doctor Qualifications"), max_length=50, default="None")
    consultations = models.TextField(_("Doctor's Applicable Consultations"))
    languages = models.CharField(_("Doctor's Known Languages"), max_length=100, default="None")

class Doctor(User):
    objects = DoctorManager()

    @property
    def more(self):
        return self.doctorinfo
    
    class Meta:
        proxy = True

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