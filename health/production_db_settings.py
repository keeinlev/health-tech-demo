from .settings import *
from django.core.exceptions import ImproperlyConfigured
import environ

try:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql_psycopg2',
            'NAME': env('RDS_NAME'),
            'USER': env('RDS_USER'),
            'PASSWORD': env('RDS_PASSWORD'),
            'HOST': env('RDS_ENDPOINT'),
            'PORT': env('RDS_PORT'),
        }
    }
except ImproperlyConfigured:
    from .development_db_settings import DATABASES as dbs
    DATABASES = dbs