from datetime import datetime, timedelta
from apscheduler.schedulers.background import BackgroundScheduler
from .remindupcoming import remindAllUpcoming

def test():
    print('hello')

def start():
    s = BackgroundScheduler()
    s.add_job(remindAllUpcoming, 'interval', minutes=1)
    s.start()
    #print('uncomment these later in scheduledreminders.updater line 9-11')