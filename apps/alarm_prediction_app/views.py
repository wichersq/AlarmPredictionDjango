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

from googleapiclient.discovery import build
import pprint
# TODO: fix it to work with ajax
pp = pprint.PrettyPrinter(indent=2)
STATES_ARR = ["AL", "AK", "AZ", "AR", "CA", "CO", "CT", "DE", "FL", "GA", "HI", "ID", "IL", "IN",
              "IA", "KS", "KY", "LA", "ME", "MD", "MA", "MI", "MN", "MS", "MO", "MT", "NE", "NV", "NH", "NJ", "NM", "NY",
              "NC", "ND", "OH", "OK", "OR", "PA", "RI", "SC", "SD", "TN", "TX", "UT", "VT", "VA", "WA", "WV", "WI",
              "WY"]


def display_cover(request):
    if not request.session.__contains__('id'):
        User.managers.manager_session.clear()
        return render(request, "alarm_prediction_app/cover_page.html")
    return redirect(reverse("login_page"))


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
        return redirect(reverse("login_page"))
    if request.method == "GET":
        return "it shouldn't suppose to be here"


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
        return redirect(reverse("login_page"))
    set_up_error_message(request, errors)
    return redirect("/")
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
            request.POST, request.session['id'])
    if not errors:
        # Pop up adjust time bar
        return redirect(reverse("login_page"))
    set_up_error_message(request, errors)
    # TODO: find a way to pass confict event so we can hightlight the a row in a login_page table
    return redirect(reverse("login_page"))


def calc_alarm(request, event_id):
    if request.method == "GET":
        errors, event = User.managers.get_alarm_time(
            request.session['id'], event_id, None)
        if errors or event == None:
            set_up_error_message(request, errors)
    return redirect(reverse("login_page"))


def show_event(request, event_id):
    if request.method == "GET":
        context = {
            'event': User.managers.get_a_event(event_id, request.session['id'])
        }
        return render(request, "alarm_prediction_app/show_event.html", context)
    return redirect(reverse("login_page"))


def delete_event(request, event_id):
    if request.method == "GET":
        User.managers.delete_a_event(request.session['id'], event_id)
    return redirect(reverse("login_page"))


def display_edit_page(request, event_id):
    if request.method == 'GET':
        event = User.managers.get_a_event(event_id, request.session['id'])
        if event == None:
            return redirect(reverse("login_page"))
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
    return redirect(reverse("login_page"))


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
    return redirect(reverse("login_page"))


def get_google_events(request):
    credentials = User.managers.get_current_user(
        request.session['id']).calendar_credential
    service = build('calendar', 'v3', credentials=credentials.credential)
    # Call the Calendar API
    now = datetime.datetime.utcnow().isoformat() + 'Z'  # 'Z' indicates UTC time
    print('Getting the upcoming 10 events')
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
    return redirect(reverse("login_page"))


def get_time(request, calendar_event):
    calendar_event = {'attendees': [{'email': 'queenie.giap@gmail.com',
                              'responseStatus': 'needsAction'},
                             {'email': 'example@gmail.com',
                              'organizer': True,
                              'responseStatus': 'accepted',
                              'self': True}],
               'created': '2019-06-21T04:43:59.000Z',
               'creator': {'email': 'example@gmail.com', 'self': True},
               'description': 'Hiking at Castle Rock',
               'end': {'dateTime': '2019-06-22T11:30:00-07:00'},
               'etag': '"3122184478890000"',
               'htmlLink': 'https://www.google.com/calendar/event?eid=2lOSDJGRODwgrejjaGVyc0Bt',
               'iCalUID': 'uyguygygui@google.com',
               'id': 'wertyuio',
               'kind': 'calendar#event',
               'location': 'Stevens Creek County Park, 11401 Stevens Canyon '
                           'Rd, Cupertino, CA 95014, USA',
               'organizer': {'email': 'example@gmail.com', 'self': True},
               'reminders': {'useDefault': True},
               'sequence': 0,
               'start': {'dateTime': '2019-06-22T10:30:00-07:00'},
               'status': 'confirmed',
               'summary': 'Hiking with Friends',
               'updated': '2019-06-21T04:43:59.445Z'}

    ex_event = {'name': calendar_event['description'],
                'start_address': '150 S Taaffe St, Sunnyvale, CA 94086',
                'end_address': calendar_event['location'],
                'start_time': calendar_event['start']['dateTime'],
                'important_level': 1,
                'travel_by': 3,
                'summary': 'Hiking with Friends'}

    User.managers.g_calculate_time(request.session['id'],ex_event)
    return redirect(reverse("login_page"))
