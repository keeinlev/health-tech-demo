from django.shortcuts import render, redirect
from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse
from datetime import datetime, timedelta
from dateutil import tz, parser
from graph.auth_helper import get_sign_in_flow, get_token_from_code, store_user, remove_user_and_token, get_token
from graph.graph_helper import *
from pprint import pprint

def sign_in(request):
    # Get the sign-in flow
    flow = get_sign_in_flow()
    # Save the expected flow so we can use it in the callback
    try:
        request.session['auth_flow'] = flow
    except Exception as e:
        print(e)
    # Redirect to the Azure sign-in page
    return HttpResponseRedirect(flow['auth_uri'])

def callback(request):
    # Make the token request
    result = get_token_from_code(request)

    #Get the user's profile
    try:
        user = get_user(result['access_token'])

        # Store user
        store_user(request, user)
        pprint(user)
        print(user.get('id'))
    except KeyError as e:
        return render(request, 'index.html', {'message': 'Oops! We weren\'t able to get access to your account!'})
    return redirect('index')