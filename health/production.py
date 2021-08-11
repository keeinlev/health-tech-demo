from .settings import *

DEBUG = True

ALLOWED_HOSTS = ['127.0.0.1','health-tech.azurewebsites.net', 'localhost']

CURRENT_DOMAIN = 'health-tech.azurewebsites.net'

SESSION_COOKIE_AGE = 900
CSRF_COOKIE_SECURE = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SAMESITE = 'None'
SESSION_COOKIE_SAMESITE = 'None'