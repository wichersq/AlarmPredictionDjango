from __future__ import unicode_literals
import re
import bcrypt
import datetime
import math
import pytz

from django.db import models
from django.db.models import Q
from django.core.exceptions import ObjectDoesNotExist

from datetime import timedelta, date, datetime, timezone, tzinfo
from ..alarm_prediction_app.prediction_code.google_map_api import MapsAPI
from ..alarm_prediction_app.prediction_code.ready_time_calc import AlarmCalc
from ..alarm_prediction_app.prediction_code.ready_time_calc_ml import AlarmCalcML

from namedlist import namedlist
from django.contrib.postgres.fields import JSONField
from jsonfield import JSONField
from oauth2client.contrib.django_util.models import CredentialsField


class UserManager(models.Model):
    # ----------------------------registration and login---------------------------------------
    EMAIL_REGEX = re.compile(r'^[a-zA-Z0-9.+_-]+@[a-zA-Z0-9._-]+\.[a-zA-Z]+$')
    MESSAGE_ERROR = {'blank': 'This field is required',
                     'first': "First name should be at least 2 characters",
                     'last': "Last name should be at least 2 characters",
                     'invalid_email': 'Invalid email address!',
                     'email_taken': 'Email address is taken. Please choose another one',
                     "invalid_bd": 'Invalid birthday',
                     'age': "The user needs to be over 13 years old",
                     'confirm_pass': 'Password does not match',
                     'login_mess': 'Email and Password doesn\'t match',
                     'home_address': 'Cannot find your home address. Please check it again',
                     'email_not_there': 'No Email found', }
    REQUIRED_AGE = 13

    CREATE_OBJECT_ERROR = {'date': 'Event time should be in the future',
                           'name_of_event': "Name should be at least 3 characters",
                           'time_range': 'Conflict with another event',
                           'data_request': 'Invalid address. Please check origin and destination'
                           }
    api_key_file = open("API_KEY.txt", 'r')
    API_KEY = api_key_file.readline().rstrip()

    DATA_REQUEST = MapsAPI(API_KEY)
    ALARM_CALC = AlarmCalc()
    ALARM_CALC_ML = AlarmCalcML()

    def __init__(self):
        self.manager_session = {}

    # TODO: write front end validation for this
    # def has_empty_field(self, first, last, email, password,
    #                     confirm_password, errors_dict):
    #     is_valid = True
    #     if len(first) < 2:
    #         errors_dict["fn_error"] = self.MESSAGE_ERROR['first']
    #         is_valid = False
    #     if len(last) < 2:
    #         errors_dict["ln_error"] = self.MESSAGE_ERROR['last']
    #         is_valid = False
    #     if not self.EMAIL_REGEX.match(email):
    #         errors_dict["e_error"] = self.MESSAGE_ERROR['invalid_email']
    #         is_valid = False
    #     if not password:
    #         errors_dict["p_error"] = self.MESSAGE_ERROR['blank']
    #         is_valid = False
    #     else:
    #       is_valid = match_confirm_password
    #     return is_valid

    def match_confirm_password(self, password, confirm_password, errors_dict):
        if password != confirm_password:
            errors_dict["cp_error"] = self.MESSAGE_ERROR['confirm_pass']
            return False
        return True

    def basic_validator(self, post_data):
        errors = {}
        # TODO: can delete if do front end validation
        # has_no_empty_field = self.has_empty_field(self.manager_session['first'],
        #                                           self.manager_session['last'],
        #                                           self.manager_session['email'],
        #                                           self.manager_session['password'],
        #                                           confirm_pass, errors)
        has_no_empty_field = True
        if has_no_empty_field \
                and self.check_age(post_data['birthday'], errors) \
                and self.match_confirm_password(post_data['con_pass'], post_data['pass'], errors):
            if self.has_email(post_data['email']):
                errors['e_error'] = self.MESSAGE_ERROR['email_taken']
        # if errors:
        #     self.manager_session.clear()
        return errors

    def has_email(self, email):
        try:
            user = User.objects.get(email=email)
        except ObjectDoesNotExist:
            return None
        return user

    def check_age(self, birthday, errors):
        birthday = datetime.strptime(birthday, '%Y-%m-%d')
        is_valid = True
        today = date.today()
        age = today.year - birthday.year - \
            ((today.month, today.day) < (birthday.month, birthday.day))
        if age < 0:
            errors['b_error'] = self.MESSAGE_ERROR['invalid_bd']
        elif age < self.REQUIRED_AGE:
            errors['b_error'] = self.MESSAGE_ERROR['age']
            is_valid = False
        return is_valid

    def get_home_address(self, post_data, error_dict):
        address = f"{post_data['address']} {post_data['address2']}, {post_data['city']}, {post_data['state']} {post_data['zip']}"
        print(address)
        try:
            self.DATA_REQUEST.get_place_id(address)
        except ValueError as identifier:
            error_dict['adr_error'] = self.MESSAGE_ERROR['home_address']
            return ''
        return address

    def register_user(self, post_data):
        errors = self.basic_validator(post_data)
        user = None
        if not errors:
            address = self.get_home_address(post_data, errors)
            if address:
                password = bcrypt.hashpw(
                    post_data['pass'].encode('utf-8'), bcrypt.gensalt())

                user = User.objects.create(first_name=post_data['first'],
                                           last_name=post_data['last'],
                                           email=post_data['email'],
                                           password=password,
                                           birthday=post_data['birthday'],
                                           gender=post_data['gender'],
                                           home_address=address)
                Credential.objects.create(credential=None, user=user)
                print("****************************user.calendar_credential**********************",user.calendar_credential)
        self.manager_session['user'] = user
        return errors, user

    def validator_login_field(self, email, errors_dict):
        user = None
        # FIXME: this doesn't need to check regex since front end validation
        if not self.EMAIL_REGEX.match(email):
            errors_dict["login_error"] = self.MESSAGE_ERROR['invalid_email']
        else:
            user = self.has_email(email)
        return user

    def verify_login_info(self, post_data):
        errors = {}
        email = post_data['email']
        user_info = self.validator_login_field(email, errors)
        if user_info == None:
            errors['login_error'] = self.MESSAGE_ERROR['email_not_there']
        else:
            password = post_data["pass"].encode('utf-8')
            checking_password = user_info.password.encode('utf-8')

            if bcrypt.checkpw(password, checking_password):
                self.manager_session['user'] = user_info
            else:
                errors['login_error'] = self.MESSAGE_ERROR['login_mess']

        return errors, user_info

    def get_current_user(self, id):
        if 'user' in self.manager_session and self.manager_session['user'].id == id:
            return self.manager_session['user']
        try:
            user = User.objects.get(id=id)
            self.manager_session['user'] = user
            return user
        except ObjectDoesNotExist:
            return None
    # ----------------------------endValidation---------------------------------------
# TODO: Validating add new event, find a way to validate address

    def save_calendar_credential(self, user_id, credential):
        current_user = self.get_current_user(user_id)
        if not current_user.has_credential():
            current_user.set_credential(credential)
            # Credential.objects.create(credential=credential, user=current_user)

    def get_a_event(self, event_id, user_id):
        event = None
        try:
            event = Event.objects.get(id=event_id)

        except ObjectDoesNotExist:
            return event

        if event.creator.id != user_id:
            event = None
        return event

    def get_all_events(self, user_id):
        current_user = self.get_current_user(user_id)
        events = current_user.events.all().order_by('-created_at')
        return events

    def validate_event(self, name, start, dest, start_time):
        errors = {}
        if len(name) < 3:
            errors['n_error'] = self.CREATE_OBJECT_ERROR['name_of_event']
        if not dest:
            errors['e_error'] = self.MESSAGE_ERROR['blank']
        if not start:
            errors['s_error'] = self.MESSAGE_ERROR['blank']
        if not start_time:
            errors['st_error'] = self.MESSAGE_ERROR['blank']
            print(errors['st_error'])
        else:
            today = datetime.now(pytz.timezone('US/Pacific'))
            start_time = self.convert_start_time(start_time)
            print(type(today))
            if start_time < today:
                errors['st_error'] = self.CREATE_OBJECT_ERROR['date']
        return errors

    # def check_schedule(self, start_time, end_time, current_user, errors):
    #     start_time = datetime.strptime(start_time, '%Y-%m-%dT%H:%M')
    #     end_time = datetime.strptime(end_time, '%Y-%m-%dT%H:%M')
    #     s_range = start_time.date()
    #     e_range = end_time.date()
    #     events = Event.objects.filter(Q(alarm__range=(s_range, e_range)) | Q(
    #         start_time__range=(s_range, e_range)) | Q(end_time__range=(s_range, e_range)))
    #     events = events.filter(creator=current_user)
    #     # FIXME:FIXME:FIXME:FIXME:FIXME:FIXME:FIXME:FIXME:FIXME:FIXME:FIXME:FIXME:
    #     # for event in events:
    #     #     s_time = event.start_time
    #     #     e_time = event.end_time
    #     #     if event.alarm != None:
    #     #         s_time = event.alarm
    #     # https://stackoverflow.com/questions/9044084/efficient-date-range-overlap-calculation-in-python
    #     #     latest_s = max(start_time, s_time)
    #     #     earliest_e = min(end_time, e_time)
    #     #     if earliest_e > latest_s:
    #     #         errors['tr_error'] = self.CREATE_OBJECT_ERROR['time_range']
    #     #         return event

    def create_event(self, post_data, user_id):
        name = post_data['name']
        start = post_data['start_address']
        dest = post_data['end_address']
        start_time = post_data['start_time']
        importance_level = post_data['importance_level']
        travel_by = post_data['travel_by']
        print('start_time', type(start_time))
        errors = self.validate_event(name, start, dest, start_time)
        event = None
        current_user = self.get_current_user(user_id)
        if not errors:
            event = Event.objects.create(
                name=name, creator=current_user, start_address=start,
                end_address=dest, importance_level=importance_level, start_time=start_time, travel_by=travel_by)
            Place.objects.create(event=event)
        return errors, event

        # This will use ml model

    def g_calculate_time(self, user_id, event_info):
        print('in model g_calculate_time')
        # self.create_event(event_info, user_id)
        event = event_info
        event['travel_duration'] = 840
        event['travel_distance'] = 14162
        event['dest_place'] = {'price_level': None,
                               'reviews': 444,
                               'rating': 4.6}
        self.ALARM_CALC_ML.calc_alarm_time(event)

        # errors, event = self.create_event(event_info, user_id)
        # if errors:
        #     # TODO: display to html
        #     pass
        # else:
        #     self.DATA_REQUEST.get_place_info(event.dest_place, event.end_address)

    def edit_an_event(self, post_data, user_id, event_id):
        errors = {}
        name = post_data['name']
        start = post_data['start_address']
        dest = post_data['end_address']
        start_time = post_data['start_time']
        event = self.get_a_event(event_id, user_id)
        if event != None:
            errors = self.validate_event(name, start, dest, start_time)
            # event = self.check_schedule(start_time,end_time, current_user, errors)
            if not errors:
                call_api_needed, re_calc_needed = self.is_anything_changed(
                    post_data, event)
                errors, event = self.update_an_event(
                    event, call_api_needed, re_calc_needed, post_data)
        return errors, event

    def is_anything_changed(self, post_data, event):
        call_api_needed = False
        re_calc_needed = False
        if event.alarm != None:
            if event.start_address != post_data['start_address']:
                print(event.start_address, post_data['start_address'])
                call_api_needed = True
            elif event.end_address != post_data['end_address']:
                print(event.end_address, post_data['end_address'])
                call_api_needed = True
            elif event.start_time.strftime("%Y-%m-%dT%H:%M") != post_data['start_time']:
                print(event.start_time.strftime(
                    "%Y-%m-%dT%H:%M"), post_data['start_time'])
                call_api_needed = True
            elif event.travel_by != int(post_data['travel_by']):
                print(event.travel_by, post_data['travel_by'])
                call_api_needed = True
            elif event.importance_level != post_data['important_lv']:
                re_calc_needed = True
            print("re_calc_needed", re_calc_needed)
            print("call_api_needed", call_api_needed)
        return call_api_needed, re_calc_needed

    def update_an_event(self, event, call_api, re_calc, post_data):
        print('model update_an_event')
        errors = {}
        event.name = post_data['name']
        event.start_address = post_data['start_address']
        event.end_address = post_data['end_address']
        event.start_time = self.convert_start_time(post_data['start_time'])
        event.importance_level = int(post_data['important_lv'])
        event.travel_by = int(post_data['travel_by'])
        print(event.travel_by)
        if call_api:
            errors, event = self.get_alarm_time(
                event.creator.id, event.id, event)
        elif re_calc:
            print('update_alarm_time')
            self.update_alarm_time(event)
        event.save()
        print('errors', errors, event.end_address)
        return errors, event

    def convert_start_time(self, str_time):
        start_time = datetime.strptime(str_time, '%Y-%m-%dT%H:%M')
        start_time = pytz.timezone('US/Pacific').localize(start_time)
        print("convert_start_time start_time", type(start_time))
        return start_time

    def get_alarm_time(self, user_id, event_id, event):
        errors = {}
        print('get_alarm_time_method')
        if event == None:
            event = self.get_a_event(event_id, user_id)
        print('before method', event.start_address)
        if event.creator.id == user_id:
            try:
                self.DATA_REQUEST.get_place_info(
                    event.dest_place, event.end_address)
                arrival_sec = self.ALARM_CALC.calc_sec_arrive(
                    event.dest_place.reviews, event.dest_place.price_level, event.dest_place.rating)
                print('arrival_sec', arrival_sec)
                arrival_time = event.start_time - \
                    timedelta(seconds=arrival_sec)
                print('arrival_time', arrival_time)
                event = self.DATA_REQUEST.get_time(event, arrival_time)
                print('event done')
                print('get_alarm_time', event.start_address)
                print('get_alarm_time', event.dest_place.reviews)
                event.early_arrival_sec = arrival_sec
            except ValueError as err:
                print('catch the error', err)
                errors['dq_error'] = self.CREATE_OBJECT_ERROR['data_request']
                return errors, None
            self.update_alarm_time(event)
            event.dest_place.save()
            event.save()
        return errors, event

    def update_alarm_time(self, event):
        recommended_ready_sec = self.ALARM_CALC.calc_alarm_time(event)
        event.alarm = event.start_time - \
            timedelta(seconds=recommended_ready_sec)
        print('travel time', event.travel_duration/60)
        print("recommended_ready_sec", recommended_ready_sec/60)

    def delete_a_event(self, user_id, event_id):
        is_deleted = False
        try:
            event = Event.objects.get(id=event_id)
            if event.creator.id == user_id:
                event.delete()
                is_deleted = True
        except ObjectDoesNotExist:
            return is_deleted
        return is_deleted

    # TODO: Calculate get place API and get the duration and feet in the model.

    # TODO: data request direction with arrival time
    # TODO: get the info from store first calculate arrival then call data request with event.start_time - arrival time
# ---------------------------------------------------- -----------------------------------------


class User(models.Model):
    GENDER_MALE = 1
    GENDER_FEMALE = 2
    GENDER_OTHER = 0
    GENDER_CHOICES = [(GENDER_OTHER, 'NA'), (GENDER_MALE,
                                             'Male'), (GENDER_FEMALE, 'Female')]
    first_name = models.CharField(max_length=45)
    last_name = models.CharField(max_length=45)
    email = models.CharField(max_length=255)
    birthday = models.DateField()
    password = models.TextField()
    gender = models.IntegerField(choices=GENDER_CHOICES)
    home_address = models.TextField(blank=True, default='')

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    # calendar_credential = models.CharField(
    #     max_length=255, blank=True, default='')
    managers = UserManager()

    def get_full_name(self):
        return f"{self.first_name} {self.last_name}"

    def has_credential(self):
        print(self.calendar_credential.credential)
        return self.calendar_credential.credential != None
    
    def set_credential(self, credential):
        calendar_credential = self.calendar_credential
        calendar_credential.credential = credential
        calendar_credential.save()

    def __repr__(self):
        return f"<User object: first_name : {self.first_name} | "\
            f"last_name : {self.last_name} | email: {self.email}>"


class Credential(models.Model):
    user = models.OneToOneField(
        User, related_name="calendar_credential", on_delete=models.CASCADE, primary_key=True)
    credential = CredentialsField(null=True)


class Event(models.Model):
    WALKING = 0
    CYCLING = 1
    TRANSIT = 2
    DRIVING = 3
    FLIGHT = 4
    TRANS_CHOICES = [(WALKING, 'walking'), (CYCLING, 'bicycling'),
                     (TRANSIT, 'transit'), (DRIVING, 'driving'), (FLIGHT, 'flight')]
    name = models.CharField(max_length=255)
    creator = models.ForeignKey(
        User, related_name="events", on_delete=models.CASCADE)
    start_address = models.TextField()
    end_address = models.TextField()
    start_time = models.DateTimeField()
    travel_by = models.IntegerField(choices=TRANS_CHOICES)
    importance_level = models.IntegerField()
    summary_info = models.TextField(default='', blank=True)
    alarm = models.DateTimeField(null=True, blank=True)
    travel_duration = models.IntegerField(null=True, blank=True)
    travel_distance = models.IntegerField(null=True, blank=True)
    early_arrival_sec = models.IntegerField(null=True, blank=True)
    prep_duration = models.IntegerField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __repr__(self):
        return f"<Event object: name : {self.name} | start_address : {self.start_address} | granted? : {self.start_time}>"

    def is_passed(self):
        start = self.start_time.replace()
        today = datetime.now(pytz.timezone('US/Pacific'))
        print(start,  today, start > today)
        return start < today

    def get_format_travel_duration(self):
        return self.get_format_duration(self.travel_duration)

    def get_format_prep_duration(self):
        return self.get_format_duration(self.prep_duration + self.early_arrival_sec)

    def get_format_duration(self, second):
        hour = math.floor(second/3600)
        minute = math.floor((second % 3600)/60)
        time_str = ""
        if hour > 0:
            time_str = str(hour) + " hour(s) "
        if minute > 0:
            time_str += str(minute) + " minute(s)"
        print('time_str', time_str)
        return time_str


class Place(models.Model):
    event = models.OneToOneField(Event, related_name="dest_place",
                                 on_delete=models.CASCADE,
                                 primary_key=True,
                                 )
    google_place_id = models.CharField(max_length=255, null=True, blank=True)
    name = models.CharField(max_length=255)
    address = models.TextField(null=True, blank=True)
    hours = JSONField(null=True, blank=True)
    price_level = models.IntegerField(null=True, blank=True)
    reviews = models.IntegerField(null=True, blank=True)
    rating = models.FloatField(null=True, blank=True)
    # https://docs.djangoproject.com/en/dev/ref/validators/#django.core.validators.validate_comma_separated_integer_list
    type_store = JSONField(null=True, blank=True)
    url = models.TextField(null=True, blank=True)
    website = models.TextField(null=True, blank=True)
