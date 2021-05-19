from django.apps import AppConfig


class ScheduledremindersConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'scheduledreminders'
    verbose_name = "Reminder Application"
    def ready(self):
        from . import updater
        updater.start()
