from book.models import Appointment
from book.tasks import send_reminder
from datetime import datetime, timedelta
from pytz import utc, timezone

eastern = timezone('America/New_York')

# Helper to fetch all Appointments within 15 minutes of now that are booked and have not yet had a reminder sent for them yet.
def remind_all_upcoming(): 
    now = datetime.now().astimezone(utc)
    toBeUpdated1Day = Appointment.objects.filter(datetime__lte=now+timedelta(days=1), datetime__gt=now+timedelta(minutes=30), reminder_sent=0, booked=True) # all appts between now and exactly 1 day from now,
    # ex. if someone booked an appt for exactly one day ahead, they would receive a confirmation email, then they would receive a 1 day reminder email as well, which is redundant and annoying
    # so this will make sure that doesn't happen
    toBeUpdated1Day.update(reminder_sent=1)
    toBeUpdated30Mins = Appointment.objects.filter(datetime__lte=now+timedelta(days=30), datetime__gt=now, reminder_sent=0, booked=True) # every appt booked within 30 mins of its scheduled time
    toBeUpdated30Mins.update(reminder_sent=2)
    # prevents the 30 min reminder from being sent if User books less than 30 mins before scheduled time, as confirmation email will have just been sent, User would get 2 emails right after each other
    upcoming1 = Appointment.objects.filter(datetime__lte=now+timedelta(minutes=30), datetime__gte=now, booked=True, reminder_sent=1) # all appts whose times are between now and 30 minutes from now, reminder_sent=1 means either first 1-day reminder sent already or was booked within 1 day from now
    upcoming2 = Appointment.objects.filter(datetime__lte=now+timedelta(days=1, minutes=15), datetime__gte=now+timedelta(days=1), booked=True, reminder_sent=0) # all appts between 1 day from now and 1 day 15 mins from now
    upcoming = upcoming1 | upcoming2
    for appt in upcoming:
        send_reminder(appt.id, 'remind')
        appt.reminder_sent += 1
        appt.save()

# Helper to delete any Appointments that were opened but not booked that have passed
def delete_unbooked():
    now = datetime.now().astimezone(utc)
    Appointment.objects.filter(datetime__lte=now, booked=False).delete()

# Main background scheduled job function
def update_appt_status():
    remind_all_upcoming()
    delete_unbooked()