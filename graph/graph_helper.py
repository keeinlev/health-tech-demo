import requests
import json
import logging

# These two lines enable debugging at httplib level (requests->urllib3->http.client)
# You will see the REQUEST, including HEADERS and DATA, and RESPONSE with HEADERS but without DATA.
# The only thing missing will be the response.body which is not logged.
try:
    import http.client as http_client
except ImportError:
    # Python 2
    import httplib as http_client
http_client.HTTPConnection.debuglevel = 1

# You must initialize logging, otherwise you'll not see debug output.
logging.basicConfig()
logging.getLogger().setLevel(logging.DEBUG)
requests_log = logging.getLogger("requests.packages.urllib3")
requests_log.setLevel(logging.DEBUG)
requests_log.propagate = True

graph_url = 'https://graph.microsoft.com/v1.0'

def get_user(token):
    # Send GET to /me
    user = requests.get(
        '{0}/me'.format(graph_url),
        headers={
        'Authorization': 'Bearer {0}'.format(token)
        },
        params={
        '$select': 'displayName,mail,mailboxSettings,userPrincipalName'
        })
    # Return the JSON result
    return user.json()

def get_calendar_events(token, start, end, timezone):
    # Set headers
    headers = {
        'Authorization': 'Bearer {0}'.format(token),
        'Prefer': 'outlook.timezone="{0}"'.format(timezone)
    }

    # Configure query parameters to
    # modify the results
    query_params = {
        'startDateTime': start,
        'endDateTime': end,
        '$select': 'subject,organizer,start,end',
        '$orderby': 'start/dateTime',
        '$top': '50'
    }

    # Send GET to /me/events
    events = requests.get('{0}/me/calendarview'.format(graph_url),
        headers=headers,
        params=query_params)

    # Return the JSON result
    return events.json()

def create_event(token, subject, start, end, attendees=None, body=None, timezone='UTC'):
  # Create an event object
  # https://docs.microsoft.com/graph/api/resources/event?view=graph-rest-1.0
    new_event = {
        'subject': subject,
        'start': {
            'dateTime': start,
            'timeZone': timezone
        },
        'end': {
            'dateTime': end,
            'timeZone': timezone
        }
    }

    if attendees:
        attendee_list = []
        for email in attendees:
            # Create an attendee object
            # https://docs.microsoft.com/graph/api/resources/attendee?view=graph-rest-1.0
            attendee_list.append({
                'type': 'required',
                'emailAddress': { 'address': email }
            })

        new_event['attendees'] = attendee_list

    if body:
        # Create an itemBody object
        # https://docs.microsoft.com/graph/api/resources/itembody?view=graph-rest-1.0
        new_event['body'] = {
            'contentType': 'text',
            'content': body
        }
    print('{0}/me'.format(graph_url))
  # Set headers
    headers = {
        'Authorization': 'Bearer {0}'.format(token),
        'Content-Type': 'application/json'
    }
    r=requests.post('{0}/me/calendar/events'.format(graph_url),
        headers=headers,
        data=json.dumps(new_event))