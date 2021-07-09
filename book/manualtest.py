from book.models import Appointment
from accounts.models import Doctor, Patient
from datetime import datetime, timedelta
from pytz import utc
from book.times import IntTimes
from book.views import getDateTime

today = datetime.now().astimezone(utc)
testdate = today + timedelta(days=1)
d = Doctor.objects.last()
p = Patient.objects.last()

def createTestAppts():
    for i in range(5):
        t = IntTimes.choices[i][0]
        Appointment.objects.create(doctor=d, patient=p, consultation='test', date=str(testdate.date()), time=t, datetime=getDateTime(testdate, t), booked=True)

    print(Appointment.objects.all())