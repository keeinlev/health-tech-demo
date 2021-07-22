from .settings import *

DEBUG = False

ALLOWED_HOSTS = ['127.0.0.1','health-tech.azurewebsites.net', 'localhost']

DEFAULT_FILE_STORAGE = 'storages.backends.azure_storage.AzureStorage'

STATICFILES_STORAGE = 'customstorage.custom_azure.PublicAzureStorage'

AZURE_ACCOUNT_NAME = env('AZURE_ACCOUNT_NAME')

AZURE_ACCOUNT_KEY = env('AZURE_ACCOUNT_KEY')

AZURE_CONTAINER = env('AZURE_MEDIA_CONTAINER')

AZURE_STATIC_CONTAINER = env('AZURE_STATIC_CONTAINER')

AZURE_CUSTOM_DOMAIN = f'{AZURE_ACCOUNT_NAME}.blob.core.windows.net'

AZURE_URL_EXPIRATION_SECS = 600

MEDIA_URL = f'https://{AZURE_CUSTOM_DOMAIN}/{AZURE_CONTAINER}/'

STATIC_URL = f'https://{AZURE_CUSTOM_DOMAIN}/{AZURE_STATIC_CONTAINER}/'

STATIC_ROOT = os.path.join(BASE_DIR, 'static')

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

CURRENT_DOMAIN = 'health-tech.azurewebsites.net'

CSRF_COOKIE_SECURE = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SAMESITE = 'None'
SESSION_COOKIE_SAMESITE = 'None'