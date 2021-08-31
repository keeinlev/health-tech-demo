from django.db import models
from django.urls import reverse
from accounts.models import User, Patient, Doctor
from book.times import IntTimes
import datetime
from pytz import timezone, utc

eastern = timezone('America/New_York')

# Create your models here.

class Appointment(models.Model):
    class Meta:
        unique_together = ['date', 'time', 'doctor']
    date = models.DateField(default=None)
    time = models.IntegerField(default=None, choices=IntTimes.choices)
    #time = models.CharField(max_length=3, default=None, choices=Times.choices)
    datetime = models.DateTimeField(default=None, null=True, blank=True)
    consultation = models.CharField(max_length=100, null=True, default=None, blank=True)
    booked = models.BooleanField(default=False)
    patient = models.ForeignKey(Patient, related_name="%(class)s_patient", on_delete=models.CASCADE, null=True, default=None, blank=True)
    doctor = models.ForeignKey(Doctor, related_name="%(class)s_doctor", on_delete=models.CASCADE, null=True, default=None)
    reminder_sent = models.IntegerField(default=0, choices=[(0, 'No Reminder'), (1, 'One Day Reminder'), (2, '15 Minute Reminder')]) # used as flag to know when to send emails/sms
    ms_event_created = models.BooleanField(default=False)
    meeting_id = models.CharField(unique=True, max_length=48, null=True, blank=True, default=None)
    type = models.BooleanField(default=None, blank=True, null=True, choices=[(1, 'Video'), (0, 'Phone')])

    # Returns an Appointment's datetime in the format of "<Full Day Name>, <Full Month Name> <Day 1-31> at <Hour 1-12>:<Minute><AM/PM> <Timezone Short Form>""
    @property
    def dateTime(self):
        return datetime.datetime.strftime(self.datetime.astimezone(eastern), '%A, %B %d at %I:%M%p %Z')
    
    # Returns an Appointment's datetime in the format of "<Short Day Name>, <Short Month Name> <Day 1-31> <Hour 1-12>:<Minute><AM/PM>"
    # Only used for SMS messages to shorten character length
    @property
    def shortDateTime(self):
        return datetime.datetime.strftime(self.datetime.astimezone(eastern), '%a %b %d %I:%M%p')
    
    # Returns an Appointment's datetime in the format of "<Short Month Name> <Day 1-31>"
    @property
    def shortMonthDay(self):
        return datetime.datetime.strftime(self.datetime.astimezone(eastern), '%b %d')

    # Returns an Appointment's time only in the format of "<Hour 1-12>:<Minute><AM/PM>"
    @property
    def apptTime(self):
        return datetime.datetime.strftime(self.datetime.astimezone(eastern), '%I:%M%p')
    
    # Using the Appointment unique meeting_id, returns the full MS Teams meeting link
    # Prevents the need to redundantly store the same long URL segments in our database, just the unique values
    @property
    def meeting_link(self):
        from health.settings import MS_TEAMS_MEETING_URL_1 as meet_link1, MS_TEAMS_MEETING_URL_2 as meet_link2
        return meet_link1 + self.meeting_id + meet_link2

    @property
    def meeting_redirect_link(self):
        return 'https://health-tech.azurewebsites.net' + reverse('meeting_redir', kwargs={'pk':self.pk})

    # Returns the ApptDetails object tied to the Appointment if it exists, creates a new one if it doesn't
    @property
    def details(self):
        from appointment.models import ApptDetails
        if ApptDetails.objects.filter(appt=self).exists():
            return ApptDetails.objects.get(appt=self)
        else:
            new = ApptDetails.objects.create(appt=self, date=self.date)
            return new

    @property
    def localTZ(self):
        return str(datetime.datetime.now(utc).astimezone().tzinfo)

    @property
    def getAllFiles(self):
        from appointment.models import ApptFile
        return ApptFile.objects.filter(appt=self)

    @property
    def getMedia(self):
        return self.getAllFiles.filter(file_type__in=['.png', '.jpg', '.gif', '.mp4', '.mov', '.wmv', '.avi'])
    
    @property
    def getNonMedia(self):
        return self.getAllFiles.excludes(file_type__in=['.png', '.jpg', '.gif', '.mp4', '.mov', '.wmv', '.avi'])

    @property
    def apptHasPassed(self):
        return self.datetime < datetime.datetime.now().astimezone(utc)