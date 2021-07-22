import environ
from storages.backends.azure_storage import AzureStorage

env = environ.Env()

class PublicAzureStorage(AzureStorage):
    account_name = env('AZURE_ACCOUNT_NAME')
    account_key = env('AZURE_ACCOUNT_KEY')
    azure_container = env('AZURE_STATIC_CONTAINER')
    expiration_secs = None