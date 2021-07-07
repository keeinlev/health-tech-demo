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
        #tz_info = tz.gettz('America/New_York')

        # Get midnight today in user's time zone
        # today = datetime.now(tz_info).replace(
        #     hour=0,
        #     minute=0,
        #     second=0,
        #     microsecond=0)

        # # Based on today, get the start of the week (Sunday)
        # if (today.weekday() != 6):
        #     start = today - timedelta(days=today.isoweekday())
        # else:
        #     start = today
        # end = start + timedelta(days=7)
        # events = get_calendar_events(
        #     result['access_token'],
        #     start.isoformat(timespec='seconds'),
        #     end.isoformat(timespec='seconds'),
        #     'Eastern Standard Time')
        # print('\n\nevents:\n')
        # pprint(events)
    except KeyError as e:
        print(e)
        return render(request, 'index.html', {'message': 'Oops! We weren\'t able to access your account!'})
    return redirect('index')