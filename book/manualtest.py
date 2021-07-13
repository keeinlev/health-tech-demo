from book.models import Appointment
from accounts.models import Doctor, Patient
from datetime import datetime, timedelta
from pytz import utc
from book.times import IntTimes
from doctordashboard.views import getDateTime
from appointment.models import ApptDetails

today = datetime.now().astimezone(utc)
testdate = today + timedelta(days=-2)
d = Doctor.objects.last()
p = Patient.objects.last()

def createTestAppts():
    for i in range(5):
        t = IntTimes.choices[i][0]
        a = Appointment.objects.create(doctor=d, patient=p, consultation='test', date=str(testdate.date()), time=t, datetime=getDateTime(testdate, t), booked=True)
        ApptDetails.objects.create(appt=a, date=a.date)
    print(Appointment.objects.all())