from book.models import Appointment
# This module will simply create 5 test Appointments using the last Doctor and Patient objects registered
# Can be run from the shell by importing createTestAppts from book.manualtest and calling createTestAppts()
# Day of the test Appointments can be changed for testing needs

from accounts.models import Doctor, Patient
from datetime import datetime, timedelta
from pytz import utc
from book.times import IntTimes
from doctordashboard.views import getDateTime
from appointment.models import ApptDetails

today = datetime.now().astimezone(utc)

# Change the number in the days keyword to set the day of the test Appointments relative to today (e.g. -2 for 2 days ago, 1 for tomorrow, 7 for next week, etc)
testdate = today + timedelta(days=-2)
d = Doctor.objects.last()
p = Patient.objects.last()

def createTestAppts():
    for i in range(5):
        t = IntTimes.choices[i][0]
        a = Appointment.objects.create(doctor=d, patient=p, consultation='test', date=str(testdate.date()), time=t, datetime=getDateTime(testdate, t), booked=True)
        ApptDetails.objects.create(appt=a, date=a.date)
    print(Appointment.objects.all())