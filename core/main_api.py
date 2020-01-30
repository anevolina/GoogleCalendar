import datefinder
import datetime
import re

from functools import wraps

import core.calendar_core as calendar_core
from core.exceptions import GCUnauthorisedUserError
from core.logger import GCLogger

logger = GCLogger()


def check_auth(func):
    """Decorator to quick check if we have records for given user in our database"""

    @wraps(func)
    def wraper(*args, **kwargs):
        if 'user_id' in kwargs.keys():
            check_user_settings(kwargs['user_id'])
        return func(*args, **kwargs)

    return wraper


def check_user_settings(user_id):
    """If we don't have records about given user_id - raise an error"""

    if not calendar_core.get_user_settings(user_id):
        raise GCUnauthorisedUserError('Current user doesn\'t have credentials in database')


@check_auth
def create_event(user_id, message):
    """Parse given message and try to create an event;
    Input:
        user_id - as it is in our database;
        message - text from the user
    Output:
        event_status - string; possible variants - ['CREATED', 'MISTAKE']
        start - datetime.datetime/ datetime.date - in what time event will start (what date parser found in the message)
        attendeed - [list of emails] - who will be invited to an event (who parser found in the message)
        location - string - location for an event (doesn't work for now, return empry string)"""

    attendees = find_attendees(message)
    location = find_location(message)
    start, end = get_start_end_time(message)

    try:
        event_status = calendar_core.add_event(user_id, message, start, end, attendees=attendees, location=location)

    except Exception as e:
        logger.exception(e, user_id=user_id, message=message)
        event_status = None

    return event_status, start, attendees, location


def get_start_end_time(message: str, duration=1):
    """Try to find date in a given message;
    Output:
        start_time, end_time - datetime.datetime/datetime.date - if a particular date was found; if nothing found return
            today's date;"""

    start_time_match = list(datefinder.find_dates(message))

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
    """Find all emails in a given message;
    Output:
        emails - list - all emails according to regexp pattern;"""

    emails = re.findall(r'[a-z]{1}[a-z0-9\.\-\_]*@[a-z]+\.[a-z]{2,}', message.lower())
    return emails

def find_location(message):
    """Suppose to looking for a location in the message, but I didn't figure out the rule for it"""

    return None


@check_auth
def add_calendar(user_id, calendar_name):
    """Try to fetch calendar with the given name, if nothing was found - create one;
    Input:
        user_id - as it is in our database;
        calendar_name - string;
    Output:
        status - one of ['FETCHED', 'CREATED', 'MISTAKE']"""

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
    """Set calendar to primary"""

    status = calendar_core.set_calendar_to_primary(user_id)

    return status

@check_auth
def logout(user_id):
    """Delete information about user from our database"""

    return calendar_core.del_user(user_id)


def authorise_user_step1():
    """Function returns authorization url.
    User should follow this url, and grant access to their calendar.
    At the very end Google will issue a key which you should pass to the second step."""

    auth_url = calendar_core.get_authorisation_url()

    return auth_url


def authorise_user_step2(user_id, key):
    """Function will fetch token for given user, using provided key from the previous step."""

    return calendar_core.fetch_token(user_id, key)