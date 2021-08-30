# IMPORTANT: When using external storage (i.e. when DJANGO_EXT_STORAGE is True) and making changes to static files, be sure to call
# "python manage.py collectstatic" before running the server. This will update the old versions of the files in the Azure Storage Account.
# Otherwise, the server will run using the outdated files.
# This command has been written to run automatically on deployment to the Cloud when using Github Actions, but if using BitBucket, you will
# need to do this manually on push/deploy.


from .settings import *
from django.core.exceptions import ImproperlyConfigured
from azure.storage.blob import BlockBlobService
import environ

env = environ.Env()

try:
    AZURE_ACCOUNT_NAME = env('AZURE_ACCOUNT_NAME')

    AZURE_ACCOUNT_KEY = env('AZURE_ACCOUNT_KEY')

    AZURE_CONTAINER = env('AZURE_MEDIA_CONTAINER')

    AZURE_STATIC_CONTAINER = env('AZURE_STATIC_CONTAINER')

    AZURE_CUSTOM_DOMAIN = f'{AZURE_ACCOUNT_NAME}.blob.core.windows.net'

    AZURE_URL_EXPIRATION_SECS = 600

    MEDIA_URL = f'https://{AZURE_CUSTOM_DOMAIN}/{AZURE_CONTAINER}/'

    STATIC_URL = f'https://{AZURE_CUSTOM_DOMAIN}/{AZURE_STATIC_CONTAINER}/'

    BLOB_SERVICE = BlockBlobService(account_name=AZURE_ACCOUNT_NAME, account_key=AZURE_ACCOUNT_KEY)

    DEFAULT_FILE_STORAGE = 'storages.backends.azure_storage.AzureStorage'

    STATICFILES_STORAGE = 'customstorage.custom_azure.PublicAzureStorage'

except ImproperlyConfigured:
    from development_storage_settings import MEDIA_URL as mu, STATIC_URL as su, MEDIA_ROOT as mr
    MEDIA_URL = mu
    STATIC_URL = su
    MEDIA_ROOT = mr