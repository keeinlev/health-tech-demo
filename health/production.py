from .settings import *

DEBUG = False

ALLOWED_HOSTS = ['127.0.0.1','health-tech.azurewebsites.net']

STATICFILES_STORAGE = 'storages.backends.azure_storage.AzureStorage'

AZURE_ACCOUNT_NAME = env('AZURE_ACCOUNT_NAME')

AZURE_ACCOUNT_KEY = env('AZURE_ACCOUNT_KEY')

AZURE_CONTAINER = env('AZURE_CONTAINER')

AZURE_CUSTOM_DOMAIN = f'{AZURE_ACCOUNT_NAME}.blob.core.windows.net'

STATIC_URL = f'https://{AZURE_CUSTOM_DOMAIN}/{AZURE_CONTAINER}/'

STATIC_ROOT = os.path.join(BASE_DIR, 'static')