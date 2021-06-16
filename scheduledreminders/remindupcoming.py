from book.models import Appointment
from book.tasks import send_reminder
from datetime import datetime, timedelta
from pytz import utc, timezone

eastern = timezone('America/New_York')

def remindAllUpcoming(): 
    now = datetime.now().astimezone(utc)
    upcoming = Appointment.objects.filter(datetime__lte=now+timedelta(minutes=15), datetime__gte=now, booked=True, reminder_sent=False)
    for appt in upcoming:
        send_reminder(appt.id, 'remind')
        appt.reminder_sent = True
        appt.save()