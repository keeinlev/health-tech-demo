from .settings import *

DEBUG = False

ALLOWED_HOSTS = ['127.0.0.1','health-tech.azurewebsites.net', 'localhost', 'mehealthtech-bitbucket.azurewebsites.net']

CURRENT_DOMAIN = 'health-tech.azurewebsites.net'

CURRENT_SITE_FOR_GRAPH_RD = 'https://health-tech.azurewebsites.net'

SESSION_COOKIE_AGE = 900
CSRF_COOKIE_SECURE = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SAMESITE = 'None'
SESSION_COOKIE_SAMESITE = 'None'