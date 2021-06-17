from django.apps import AppConfig


class ScheduledremindersConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'scheduledreminders'
    verbose_name = "Reminder Application"

    # Runs at app start
    def ready(self):
        # updater is an APScheduler BackgroundScheduler that calls a reminder function every minute
        from . import updater
        updater.start()
