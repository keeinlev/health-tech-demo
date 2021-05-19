from book.models import Appointment
from book.tasks import send_reminder
from datetime import datetime, timedelta

def remindAllUpcoming():
    now = datetime.utcnow()
    upcoming = Appointment.objects.filter(datetime__lte=now+timedelta(minutes=15), booked=True, reminder_sent=False)

    for appt in upcoming:
        send_reminder(appt.id, 'remind')
        appt.reminder_sent = True
        appt.save()