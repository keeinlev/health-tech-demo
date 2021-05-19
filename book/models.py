from django.db import models
from accounts.models import User, Patient, Doctor
from book.times import IntTimes
import datetime
from pytz import timezone, utc

eastern = timezone('America/New_York')

def from24hr(time):
    timestr = str(time)
    hour, rest = timeFromString(timestr)
    rest = str(rest)
    suffix = '' 
    if hour > 11:
        suffix = 'PM'
    else:
        suffix = 'AM'
    return f'{12 if (hour % 12 == 0) else hour % 12}:{rest}{suffix}'

def timeFromString(time):
    return (int(time[:-2]), time[-2:])


def from24hrInt(time):
    timestr = str(time)
    hour, rest = timeFromString(timestr)
    suffix = '' 
    if hour > 11:
        suffix = 'PM'
    else:
        suffix = 'AM'
    return f'{12 if (hour % 12 == 0) else hour % 12}:{rest}{suffix}'

def timeFromStringInt(time):
    return (int(time[:-2]), int(time[-2:]))

# Create your models here.

class Appointment(models.Model):
    class Meta:
        unique_together = ('date', 'time', 'doctor')
    date = models.DateField(default=None)
    time = models.IntegerField(default=None, choices=IntTimes.choices)
    #time = models.CharField(max_length=3, default=None, choices=Times.choices)
    datetime = models.DateTimeField(default=None, null=True, blank=True)
    consultation = models.CharField(max_length=100, null=True, default=None, blank=True)
    booked = models.BooleanField(default=False)
    patient = models.ForeignKey(Patient, related_name="%(class)s_patient", on_delete=models.CASCADE, null=True, default=None, blank=True)
    doctor = models.ForeignKey(Doctor, related_name="%(class)s_doctor", on_delete=models.CASCADE, null=True, default=None)
    reminder_sent = models.BooleanField(default=False)

    def dateTime(self):
        return datetime.datetime.strftime(self.datetime.astimezone(eastern), '%A, %B %d at %I:%M%p %Z')
    
    def dateTimeValue(self):
        d = str(self.date)
        year = int(d[:4])
        month = int(d[5:7])
        day = int(d[8:10])
        hour, mins = timeFromStringInt(self.time)

        return datetime.datetime(year, month, day, hour, mins)
    
    @property
    def getPrescription(self):
        from appointment.models import Prescription
        p = Prescription.objects.filter(appt=self)
        if (p.exists()):
            return p.first().prescription
        else:
            return None