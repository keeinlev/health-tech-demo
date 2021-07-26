from .settings import *

DEBUG = True

ALLOWED_HOSTS = ['127.0.0.1', 'localhost']

STATIC_URL = f'health/static/'

MEDIA_URL = '/health/media/'

MEDIA_ROOT = os.path.join(BASE_DIR, 'health\media\private')

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

CURRENT_DOMAIN = '127.0.0.1:8000'