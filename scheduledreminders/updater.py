from datetime import datetime, timedelta
from apscheduler.schedulers.background import BackgroundScheduler
from .remindupcoming import remindAllUpcoming

def test():
    print('hello')

# Sets up recurring task every 1 minute
def start():
    s = BackgroundScheduler()
    s.add_job(remindAllUpcoming, 'interval', minutes=1)
    s.start()
    #print('uncomment these later in scheduledreminders.updater line 9-11')