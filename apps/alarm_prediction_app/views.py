from django.shortcuts import render
import google_auth_oauthlib.flow

# Create your views here.
from django.shortcuts import render, redirect, HttpResponse
from .models import *
from oauth2client.contrib.django_util.storage import DjangoORMStorage

from django.core.urlresolvers import reverse
from django.contrib import messages
import bcrypt
import datetime
from datetime import datetime
import time
import json 
from googleapiclient.discovery import build
import pprint
# TODO: fix it to work with ajax

# from django.utils import translation

pp = pprint.PrettyPrinter(indent=2)
STATES_ARR = ["AL", "AK", "AZ", "AR", "CA", "CO", "CT", "DE", "FL", "GA", "HI", "ID", "IL", "IN",
              "IA", "KS", "KY", "LA", "ME", "MD", "MA", "MI", "MN", "MS", "MO", "MT", "NE", "NV", "NH", "NJ", "NM", "NY",
              "NC", "ND", "OH", "OK", "OR", "PA", "RI", "SC", "SD", "TN", "TX", "UT", "VT", "VA", "WA", "WV", "WI",
              "WY"]



def display_cover(request):
    if not request.session.__contains__('id'):
        User.managers.manager_session.clear()
        return render(request, "alarm_prediction_app/cover_page.html")
    return redirect(reverse("main_page"))


def index(request):
    context = {
        'states': STATES_ARR
    }
    return render(request, "alarm_prediction_app/register_page.html", context)


def logout(request):
    request.session.clear()
    User.managers.manager_session.clear()
    return redirect("/")


def register_account(request):
    # print("register_account")
    if request.method == "POST":
        error_messages, registered_user = User.managers.register_user(
            request.POST)
        if error_messages:
            # print(error_messages)
            set_up_error_message(request, error_messages)
            return redirect("/")
        else:
            # register_user = User.managers.register_user(request.POST)
            request.session['id'] = registered_user.id
        return redirect(reverse("main_page"))
    if request.method == "GET":
        return "it shouldn't suppose to get here"


def set_up_error_message(request, error_messages):
    for key, value in error_messages.items():
        messages.error(request, value, extra_tags=key)
        # messages.add_message(request,messages.INFO --ERROR --SUCCESS --Warning, "errormess"


def process_login(request):
    if request.method == "POST":
        errors, login_user, = User.managers.verify_login_info(
            request.POST)
    if not errors:
        request.session['id'] = login_user.id
        return redirect(reverse("main_page"))
    set_up_error_message(request, errors)
    return redirect("/register&login")
# -------------------------------------------------------------------------------------------------------------------


def display_login(request):
    if request.session.__contains__('id'):
        user = User.managers.get_current_user(request.session['id'])
        context = {
            'current_user': user,
            'event_list':  User.managers.get_all_events(request.session['id'])
        }
        return render(request, "alarm_prediction_app/login_page.html", context)
    else:
        return redirect(reverse("main_page"))


def process_event(request):
    if request.method == "POST":
        errors, event, = User.managers.create_event(
            request.POST, request.session['id'], False)
    if not errors:
        # Pop up adjust time bar
        return redirect(reverse("main_page"))
    set_up_error_message(request, errors)
    # TODO: find a way to pass confict event so we can hightlight the a row in a login_page table
    return redirect(reverse("main_page"))


def calc_alarm(request, event_id):
    if request.method == "GET":
        errors, event = User.managers.get_alarm_time(
            request.session['id'], event_id, None)
        if errors or event == None:
            set_up_error_message(request, errors)
    return redirect(reverse("main_page"))


def show_event(request, event_id):
    if request.method == "GET":
        context = {
            'event': User.managers.get_a_event(event_id, request.session['id'])
        }
        return render(request, "alarm_prediction_app/show_event.html", context)
    return redirect(reverse("main_page"))


def delete_event(request, event_id):
    if request.method == "GET":
        User.managers.delete_a_event(request.session['id'], event_id)
    return redirect(reverse("main_page"))


def display_edit_page(request, event_id):
    if request.method == 'GET':
        event = User.managers.get_a_event(event_id, request.session['id'])
        if event == None:
            return redirect(reverse("main_page"))
        context = {
            'event': event,
            'date': event.start_time.strftime("%Y-%m-%dT%H:%m"),
            'current_user':  User.managers.get_current_user(request.session['id'])
        }

    return render(request, "alarm_prediction_app/edit_event_page.html", context)


def update_event(request, event_id):
    if request.method == "POST":
        User.managers.edit_an_event(
            request.POST, request.session['id'], event_id)
    return redirect(reverse("main_page"))


def clear_input(request):
    # clear input  in add new event
    pass


def cal_alarm(request, id):
    pass


# -------------------------------------------------------------------------------------------
current_state = ""


def get_authorize_calendar(request):
    # Use the client_secret.json file to identify the application requesting
    # authorization. The client ID (from that file) anhttps://www.example.com/d access scopes are required.
    print("request", request)
    flow = google_auth_oauthlib.flow.Flow.from_client_secrets_file('client_secret.json',
                                                                   scopes=['https://www.googleapis.com/auth/calendar.events.readonly'])

    # Indicate where the API server will redirect the user after the user completes
    # the authorization flow. The redirect URI is required.
    flow.redirect_uri = 'https://127.0.0.1:8000/oauth2_call_back'

    # Generate URL for request to Google's OAuth 2.0 server.
    # Use kwargs to set optional request parameters.
    authorization_url, state = flow.authorization_url(
        # Enable offline access so that you can refresh an access token without
        # re-prompting the user for permission. Recommended for web server apps.
        access_type='offline',
        # Enable incremental authorization. Recommended as a best practice.
        include_granted_scopes='true')
    print("*********************state**********************", state)
    current_state = state
    print("*********************state**********************", current_state)

    return redirect(authorization_url)


def oauth2_call_back(request):
    print("request", request)
    state = current_state

    flow = google_auth_oauthlib.flow.Flow.from_client_secrets_file(
        'client_secret.json',
        scopes=['https://www.googleapis.com/auth/calendar.events.readonly'],
        state=state)
    # flow.redirect_uri = 'https://127.0.0.1:8000/user'
    flow.redirect_uri = 'https://127.0.0.1:8000/oauth2_call_back'

    authorization_response = request.build_absolute_uri()
    # authorization_response = authorization_response.replace('http', 'https')
    print("********************************authorization_response********************************",
          authorization_response)

    flow.fetch_token(authorization_response=authorization_response)
    credentials = flow.credentials
    print("********************************credentials********************************",
          credentials)

    User.managers.save_calendar_credential(request.session['id'], credentials)
    return redirect(reverse("main_page"))


def get_info_from_gcalendar(request):
    print('get_google_events')

    credentials = User.managers.get_current_user(
        request.session['id']).calendar_credential


    print('credentials', credentials)

    service = build('calendar', 'v3', credentials=credentials.credential)
    # Call the Calendar API

    # TODO: fixed this change to local time
    now = datetime.utcnow().isoformat() + 'Z'  # 'Z' indicates UTC time

    events_result = service.events().list(calendarId='primary', timeMin=now,
                                          maxResults=100, singleEvents=True,
                                          orderBy='startTime').execute()

    print("\n\n********************************events_result********************************\n")
    pp.pprint(events_result)

    print("\n\n********************************events********************************\n")

    events = events_result.get('items', [])

    if not events:
        print('No upcoming events found.')
    for event in events:
        start = event['start'].get('dateTime', event['start'].get('date'))
        print(start, event)
    # storage = DjangoORMStorage(CredentialsModel, 'id', request.user, 'credential')
    # storage.put(credential)
    print("********************************credentials********************************", credentials)

    print("********************************request.user********************************", request.user)
    return events_result

# def retjson():
#     a = { 'accessRole': 'owner',
#   'defaultReminders': [{'method': 'popup', 'minutes': 30}],
#   'etag': '"p320e98u0sbsu40g"',
#   'items': [ { 'attendees': [ { 'email': 'queenie.giap@gmail.com',
#                                 'responseStatus': 'needsAction'},
#                               { 'email': 'example@gmail.com',
#                                 'organizer': True,
#                                 'responseStatus': 'accepted',
#                                 'self': True}],
#                'created': '2019-06-21T04:43:59.000Z',
#                'creator': {'email': 'example@gmail.com', 'self': True},
#                'description': 'Hiking at Castle Rock',
#                'end': {'dateTime': '2019-06-22T11:30:00-07:00'},
#                'etag': '"3122184478890000"',
#                'htmlLink': 'https://www.google.com/calendar/event?eid=Mmw0b2hoMHRmY3Y4ZTMxbmc2bm45ODIxdTEgcXV5ZW4ud2ljaGVyc0Bt',
#                'iCalUID': '2l4ohh0tfcv8e31ng6nn9821u1@google.com',
#                'id': '2l4ohh0tfcv8e31ng6nn9821u1',
#                'kind': 'calendar#event',
#                'location': 'Stevens Creek County Park, 11401 Stevens Canyon '
#                            'Rd, Cupertino, CA 95014, USA',
#                'organizer': {'email': 'example@gmail.com', 'self': True},
#                'reminders': {'useDefault': True},
#                'sequence': 0,
#                'start': {'dateTime': '2019-06-22T10:30:00-07:00'},
#                'status': 'confirmed',
#                'summary': 'Hiking with Friends',
#                'updated': '2019-06-21T04:43:59.445Z'},
#              { 'created': '2019-06-21T04:46:22.000Z',
#                'creator': {'email': 'example@gmail.com', 'self': True},
#                'description': "Dinner with Nev's cousin",
#                'end': {'dateTime': '2019-06-22T20:00:00-07:00'},
#                'etag': '"3122184765242000"',
#                'htmlLink': 'https://www.google.com/calendar/event?eid=NGpybjkxdDF1c2pvMm1mcjA0aGZmcWIwbzAgcXV5ZW4ud2ljaGVyc0Bt',
#                'iCalUID': '4jrn91t1usjo2mfr04hffqb0o0@google.com',
#                'id': '4jrn91t1usjo2mfr04hffqb0o0',
#                'kind': 'calendar#event',
#                'location': 'Pho Lovers, 253 E Maude Ave, Sunnyvale, CA 94085, '
#                            'USA',
#                'organizer': {'email': 'example@gmail.com', 'self': True},
#                'reminders': {'useDefault': True},
#                'sequence': 0,
#                'start': {'dateTime': '2019-06-22T19:00:00-07:00'},
#                'status': 'confirmed',
#                'summary': 'Dinner ',
#                'updated': '2019-06-21T04:46:22.621Z'},
#              { 'created': '2019-06-21T04:47:14.000Z',
#                'creator': {'email': 'example@gmail.com', 'self': True},
#                'end': {'dateTime': '2019-06-23T12:30:00-07:00'},
#                'etag': '"3122184869504000"',
#                'htmlLink': 'https://www.google.com/calendar/event?eid=MzducTVqNnMyOHM0YnBrZ2loMXVzbzBudmggcXV5ZW4ud2ljaGVyc0Bt',
#                'iCalUID': '37nq5j6s28s4bpkgih1uso0nvh@google.com',
#                'id': '37nq5j6s28s4bpkgih1uso0nvh',
#                'kind': 'calendar#event',
#                'location': 'Starbucks, 175 E El Camino Real, Mountain View, CA '
#                            '94040, USA',
#                'organizer': {'email': 'example@gmail.com', 'self': True},
#                'reminders': {'useDefault': True},
#                'sequence': 0,
#                'start': {'dateTime': '2019-06-23T11:30:00-07:00'},
#                'status': 'confirmed',
#                'summary': 'Meeting with Dylan ',
#                'updated': '2019-06-21T04:47:14.752Z'},
#              { 'attendees': [ { 'email': 'example@gmail.com',
#                                 'responseStatus': 'accepted',
#                                 'self': True}],
#                'created': '2019-06-10T22:34:10.000Z',
#                'creator': {'email': 'example@gmail.com', 'self': True},
#                'description': 'To see detailed information for automatically '
#                               'created events like this one, use the official '
#                               'Google Calendar app. https://g.co/calendar\n'
#                               '\n'
#                               'This event was created from an email you '
#                               'received in Gmail. '
#                               'https://mail.google.com/mail?extsrc=cal&plid=ACUX6DNjx2VqxXwUnzudSr71YSBjBMco6n8E1o0\n',
#                'end': {'dateTime': '2019-07-05T19:55:00-07:00'},
#                'etag': '"3120412101631000"',
#                'guestsCanInviteOthers': False,
#                'htmlLink': 'https://www.google.com/calendar/event?eid=XzZ0bG5hcXJsZTVwNmNwYjRkaG1qNHBocGVocG1pcTFpZWxoamlxMzU2ZHBqY2RyM2M1bTNhcmIyNjFqMzJkamxjOWptNmMzNGUxZ204ZWJrZWtwM2dzMWljOHI3NnByNjZrb21tc2I4ZHRuajAgcXV5ZW4ud2ljaGVyc0Bt',
#                'iCalUID': '7kukuqrfedlm2f9tsih2uc9he3s67cal5mb0f16ubgc0dpad9tu28p2b6sgf51kqhoo0',
#                'id': '_6tlnaqrle5p6cpb4dhmj4phpehpmiq1ielhjiq356dpjcdr3c5m3arb261j32djlc9jm6c34e1gm8ebkekp3gs1ic8r76pr66kommsb8dtnj0',
#                'kind': 'calendar#event',
#                'location': 'San Jose SJC',
#                'organizer': {'email': 'unknownorganizer@calendar.google.com'},
#                'privateCopy': True,
#                'reminders': {'useDefault': False},
#                'sequence': 0,
#                'source': { 'title': '',
#                            'url': 'https://mail.google.com/mail?extsrc=cal&plid=ACUX6DNjx2VqxXwUnzudSr71YSBjBMco6n8E1o0'},
#                'start': {'dateTime': '2019-07-05T17:45:00-07:00'},
#                'status': 'confirmed',
#                'summary': 'Flight to Everett (AS 2741)',
#                'transparency': 'transparent',
#                'updated': '2019-06-10T22:34:10.857Z',
#                'visibility': 'private'},
#              { 'attendees': [ { 'email': 'example@gmail.com',
#                                 'responseStatus': 'accepted',
#                                 'self': True}],
#                'created': '2019-06-10T22:34:10.000Z',
#                'creator': {'email': 'example@gmail.com', 'self': True},
#                'description': 'To see detailed information for automatically '
#                               'created events like this one, use the official '
#                               'Google Calendar app. https://g.co/calendar\n'
#                               '\n'
#                               'This event was created from an email you '
#                               'received in Gmail. '
#                               'https://mail.google.com/mail?extsrc=cal&plid=ACUX6DNjx2VqxXwUnzudSr71YSBjBMco6n8E1o0\n',
#                'end': {'dateTime': '2019-07-20T09:40:00-07:00'},
#                'etag': '"3120412101631000"',
#                'guestsCanInviteOthers': False,
#                'htmlLink': 'https://www.google.com/calendar/event?eid=XzZ0bG5hcXJsZTVwNmNwYjRkaG1qNHBocGVnb21lczMzY2RuNjRzYmFjZHBtdW9yOTYxajZxc3BtZGNzNzBzajZkdGszNnNiaDYxazM4cnI5ZGxsbjJyaG82Y3FtNGNqYjZzcjc0c2o3NmhpbWUgcXV5ZW4ud2ljaGVyc0Bt',
#                'iCalUID': '7kukuqrfedlm2f9t1gpccnbqjcsoci0fms6k8prfoh3qq0h4oimkqn835b2k76rrg4eg',
#                'id': '_6tlnaqrle5p6cpb4dhmj4phpegomes33cdn64sbacdpmuor961j6qspmdcs70sj6dtk36sbh61k38rr9dlln2rho6cqm4cjb6sr74sj76hime',
#                'kind': 'calendar#event',
#                'location': 'Everett PAE',
#                'organizer': {'email': 'unknownorganizer@calendar.google.com'},
#                'privateCopy': True,
#                'reminders': {'useDefault': False},
#                'sequence': 0,
#                'source': { 'title': '',
#                            'url': 'https://mail.google.com/mail?extsrc=cal&plid=ACUX6DNjx2VqxXwUnzudSr71YSBjBMco6n8E1o0'},
#                'start': {'dateTime': '2019-07-20T07:30:00-07:00'},
#                'status': 'confirmed',
#                'summary': 'Flight to San Jose (AS 2740)',
#                'transparency': 'transparent',
#                'updated': '2019-06-10T22:34:10.857Z',
#                'visibility': 'private'}],
#   'kind': 'calendar#events',
#   'summary': 'example@gmail.com',
#   'timeZone': 'America/Los_Angeles',
#   'updated': '2019-06-21T04:47:14.752Z'}
#     return a

def get_g_events(request):
    google_events = get_json(request)
    context = {'g_events': google_events,
               'current_user':  User.managers.get_current_user(request.session['id'])
               }
    return render(request, "alarm_prediction_app/show_g_events_page.html", context)

# put api info in json and return the info
def get_json(request):
    jsonObj = get_info_from_gcalendar(request)
    # jsonObj = retjson()

    with open('apps/alarm_prediction_app/static/alarm_prediction_app/data.txt', 'w') as outfile:  
        json.dump(jsonObj, outfile)
    return jsonObj["items"]

def show_g_events(request, index, g_event_id):
    event_details = get_data_from_jsonfile(g_event_id)
    context = {
        'event_details' : event_details
    }
    return render(request, "alarm_prediction_app/event_details.html", context)

def display_gcalendar_form(request, g_event_id):
    event_details = get_data_from_jsonfile(g_event_id)
    print("*************display_gcalendar_form***************", request.POST)
    if request.method == "GET":
        context = {
            'event_details' : event_details
        }
        return render(request, "alarm_prediction_app/create_alarm.html", context)
    else:
        print("*********display_gcalendar_form***************")
        User.managers.g_calculate_time(request.session['id'], request.POST)
        return redirect(reverse("main_page"))
    # return redirect(reverse("main_page"))

def get_data_from_jsonfile(g_event_id):
    with open('apps/alarm_prediction_app/static/alarm_prediction_app/data.txt') as json_file:  
        data = json.load(json_file)
    event_details = {}
    found = False
    for eventInfo in data['items']:
        print('id: ' + eventInfo['id'])
        if eventInfo['id']== g_event_id:
            event_details['id'] = eventInfo['id']
            event_details['start_date'] = eventInfo['start']['dateTime']
            # event_details['start_date'] = datetime.fromisoformat(eventInfo['start']['dateTime']).strftime("%m/%d/%y %H:%M:%S")
            event_details['end_date'] = eventInfo['end']['dateTime']
            # event_details['end_date'] = datetime.fromisoformat(end_date_str).strftime("%m/%d/%y %H:%M:%S")
            event_details['summary'] = eventInfo['summary']
            event_details['location'] = eventInfo['location']
            if 'attendees' in eventInfo:
                event_details['attendees'] = eventInfo['attendees']
            found = True
        if found:
            break
    return event_details
