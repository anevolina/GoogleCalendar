import datefinder
import datetime
import re

from functools import wraps

import core.calendar_core as calendar_core
from core.exceptions import GCUnauthorisedUserError


def check_auth(func):

    @wraps(func)
    def wraper(*args, **kwargs):
        if 'user_id' in kwargs.keys():
            check_user_settings(kwargs['user_id'])
        return func(*args, **kwargs)

    return wraper


def check_user_settings(user_id):
    if not calendar_core.get_user_settings(user_id):
        raise GCUnauthorisedUserError('Current user doesn\'t have credentials in database')


@check_auth
def create_event(user_id, message):

    attendees = find_attendees(message)
    location = find_location(message)
    start, end = get_start_end_time(message)

    try:
        event_status = calendar_core.add_event(user_id, message, start, end, attendees=attendees, location=location)
    except Exception as e:
        #Log Exception
        print(e)

    return event_status, start, attendees, location


def get_start_end_time(start_time: str, duration=1):

    start_time_match = list(datefinder.find_dates(start_time))

    if start_time_match and start_time_match[0].hour:
        start_time = start_time_match[0]
        end_time = (start_time_match[0] + datetime.timedelta(hours=duration))

    elif start_time_match:
        start_time = start_time_match[0].date()
        end_time = start_time_match[0].date() + datetime.timedelta(days=duration)

    else:
        start_time = end_time = datetime.datetime.now().date()

    return start_time, end_time

def find_attendees(message):
    emails = re.findall(r'[a-z]{1}[a-z0-9\.\-\_]*@[a-z]+\.[a-z]{2,}', message.lower())
    return emails

def find_location(message):

    return None


@check_auth
def add_calendar(user_id, calendar_name):
    fetched = calendar_core.fetch_calendar(user_id, calendar_name)

    status = 'FETCHED'

    if not fetched:
            created = calendar_core.create_calendar(user_id, calendar_name)
            if created:
                status = 'CREATED'
            else:
                status = 'MISTAKE'

    return status


@check_auth
def unbind_calendar(user_id):
    status = calendar_core.set_calendar_to_primary(user_id)

    return status


def authorise_user_step1():

    auth_url = calendar_core.get_authorisation_url()

    return auth_url


def authorise_user_step2(user_id, key):

    return calendar_core.fetch_token(user_id, key)
