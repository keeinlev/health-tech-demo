from .settings import *
from azure.storage.blob import BlockBlobService
import environ

env = environ.Env()

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

BLOB_SERVICE = BlockBlobService(account_name=AZURE_ACCOUNT_NAME, account_key=AZURE_ACCOUNT_KEY)