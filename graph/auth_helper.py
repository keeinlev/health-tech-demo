import msal
import os
import time
from accounts.models import Doctor
import environ
from django.core.exceptions import ImproperlyConfigured
from django.conf import settings

env = environ.Env()

try:
    settings = {
        'app_id': env('MS_GRAPH_CLIENT_ID'),
        'app_secret': env('MS_GRAPH_CLIENT_SECRET'),
        'redirect': settings.CURRENT_SITE_FOR_GRAPH_RD + env('MS_GRAPH_REDIRECT_URL'),
        'scopes' : ['user.read','mailboxsettings.read','calendars.readwrite'],
        'authority': "https://login.microsoftonline.com/common",
    }
except ImproperlyConfigured:
    settings = {
        'app_id': '',
        'app_secret': '',
        'redirect': '',
        'scopes' : '',
        'authority': '',
    }
    


def load_cache(request):
    # Check for a token cache in the session
    cache = msal.SerializableTokenCache()
    if request.session.get('token_cache'):
        cache.deserialize(request.session['token_cache'])

    return cache

def save_cache(request, cache):
    # If cache has changed, persist back to session
    if cache.has_state_changed:
        request.session['token_cache'] = cache.serialize()

def get_msal_app(cache=None):
    # Initialize the MSAL confidential client
    auth_app = msal.ConfidentialClientApplication(
        settings['app_id'],
        authority=settings['authority'],
        client_credential=settings['app_secret'],
        token_cache=cache)

    return auth_app

# Method to generate a sign-in flow
def get_sign_in_flow():
    auth_app = get_msal_app()

    return auth_app.initiate_auth_code_flow(
        settings['scopes'],
        redirect_uri=settings['redirect'])

# Method to exchange auth code for access token
def get_token_from_code(request):
    cache = load_cache(request)
    auth_app = get_msal_app(cache)

    # Get the flow saved in session
    flow = request.session.pop('auth_flow', {})

    result = auth_app.acquire_token_by_auth_code_flow(flow, request.GET)
    save_cache(request, cache)

    return result

def store_user(request, user):
    try:
        u = request.user
        u.ms_authenticated = True
        u.save()
    except Exception as e:
        print(e)

def get_token(request):
    cache = load_cache(request)
    auth_app = get_msal_app(cache)

    accounts = auth_app.get_accounts()
    if accounts:
        result = auth_app.acquire_token_silent(
            settings['scopes'],
            account=accounts[0])

        save_cache(request, cache)

        return result['access_token']

def remove_user_and_token(request):
    remove_token(request)
    if 'user' in request.session:
        del request.session['user']

def remove_token(request):
    u = request.user
    u.ms_authenticated = False
    u.save()
    if 'token_cache' in request.session:
        del request.session['token_cache']
