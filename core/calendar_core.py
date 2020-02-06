"""Core module to communicate with Google Calendar API"""

import datetime
import pickle
import os

from pymongo import MongoClient
from google_auth_oauthlib.flow import Flow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from core.logger import GCLogger

MongoDB = 'mongodb://localhost:27017/'

def get_authorisation_url():
    """The first step to authorize with URL - is to generate it.
    Output:
        auth_url - a user should follow this URL, and get authorization code at the very end;"""

    flow = get_flow()
    auth_url, _ = flow.authorization_url(prompt='consent')

    return auth_url


def fetch_token(user_id, code):
    """The second step to authorize with URL - is to check the returned code.
    Input:
        user_id - user_id as it will be in the database;
        code - code, given to the user after following auth_url;
    Output:
        True/False - whether authorization succeeded or not;"""
    flow = get_flow()

    try:
        flow.fetch_token(code=code)
        credentials = flow.credentials
        save_user(user_id, credentials=pickle.dumps(credentials))
        return True

    except Exception as e:
        logger.exception(e, user_id=user_id, code=code)
        return False


def get_flow():
    """Return flow for authorization with necessary scopes"""

    scopes = ['https://www.googleapis.com/auth/calendar']

    client_secret = get_path('client_secret.json')

    flow = Flow.from_client_secrets_file(
        client_secret,
        scopes=scopes,
        redirect_uri='urn:ietf:wg:oauth:2.0:oob')

    return flow


def get_path(file_name):
    """Return full path to the file with given file_name, located at the same directory"""

    path = os.path.dirname(os.path.abspath(__file__))
    file_name = os.path.join(path, file_name)

    return file_name


def connect_db():
    """Return connection to the database with user settings"""

    m_client = MongoClient(MongoDB)
    conn = m_client.add_event_settings

    return conn


def save_user(user_id, **kwargs):
    """Commit user settings to the database;
    Input:
        user_id - user id as it is in the database;
        **kwargs - columns to save; accepted keys = [credentials, time_zone, calendar_id];"""

    settings = connect_db()
    save_settings(settings, user_id, **kwargs)


def save_settings(settings, user_id, **kwargs):
    """save user settings;
    Input:
        settings - connection to database with settings;
        user_id - user id as it is in the database;
        **kwargs - column names(keys) and values to save; accepted keys = [credentials, time_zone, calendar_id];"""

    settings.settings.update_one({'_id': user_id}, {"$set": kwargs}, True)


def create_calendar(user_id, calendar_name, service=None):
    """Create new calendar in authorized Google Calendars account.
    Inherit time_zone from saved settings or from the primary calendar
    Input:
        user_id - user id as it is in the database;
        calendar_name - a name for the new calendar;
        service - in case we already have built calendar service;
    Output:
        True/False - whether operation succeeded or not;"""

    settings = get_user_settings(user_id)

    credentials = settings.get('credentials')
    time_zone = settings.get('time_zone')

    credentials = pickle.loads(credentials)

    service = service or get_calendar_sevice(user_id, credentials=credentials)

    if not time_zone:
        time_zone = get_calendar_time_zone(user_id, service=service)

    calendar = {
        'summary': calendar_name,
        'timeZone': time_zone
    }

    try:
        created_calendar = service.calendars().insert(body=calendar).execute()
        calendar_id = created_calendar['id']
        save_user(user_id, calendar_id=calendar_id, time_zone=time_zone)

    except HttpError as err:
        logger.error(err, user_id=user_id, calendar_name=calendar_name)
        calendar_id = None

    return calendar_id is not None


def fetch_calendar(user_id, calendar_name):
    """Try to fetch calendar by the given name - in case user wants to bind existed calendar.
    Plus save it to user settings;
    Input:
        user_id - user id as it is in the database;
        calendar_name - space-sensitive... overall very sensitive - make sure you type it right,
            or there will be two calendars with almost identical names;
    Output:
        True/False - whether operation succeeded or not; """

    calendar_id = get_calendar_id(user_id, calendar_name)

    time_zone = get_calendar_time_zone(user_id, calendar_id=calendar_id)

    save_user(user_id, calendar_id=calendar_id, time_zone=time_zone)
    return calendar_id is not None


def get_calendar_id(user_id, calendar_name):
    """Get a list of all calendar ids from the user account, and looking for id with a particular name;
    Input:
        user_id - user id as it is in the database;
        calendar_name - not case-sensitive - it compares everything in lowercase;
    Output:
        calendar_id - if the calendar was found;
        None - if the calendar isn't found by the given name; """

    credentials = get_credentials(user_id)

    service = get_calendar_sevice(user_id, credentials=credentials)

    page_token = None

    while True:
        calendar_list = service.calendarList().list(pageToken=page_token).execute()
        for calendar_list_entry in calendar_list['items']:
            if calendar_list_entry['summary'].lower() == calendar_name.lower():
                return calendar_list_entry['id']

        page_token = calendar_list.get('nextPageToken')
        if not page_token:
            break

    return None


def get_user_settings(user_id):
    """Get settings from our database by given user_id"""

    settings = connect_db()

    result = settings.settings.find_one({'_id': {'$eq': user_id}})

    return result


def get_formated_start_end_time(start_time, end_time, time_zone):
    """Get start and end time with formatting to add event;
    Input:
        start_time, end_time - datetime.datetime/ datetime.date - start and end time for an event;
    Output:
        start, end - dict - formatted time"""

    start = {'timeZone': time_zone}
    end = {'timeZone': time_zone}

    if isinstance(start_time, datetime.datetime):
        start['dateTime'] = start_time.strftime('%Y-%m-%dT%H:%M:%S')
        end['dateTime'] = end_time.strftime('%Y-%m-%dT%H:%M:%S')


    elif isinstance(start_time, datetime.date):
        start['date'] = start_time.strftime('%Y-%m-%d')
        end['date'] = end_time.strftime('%Y-%m-%d')

    return start, end


def get_calendar_time_zone(user_id, calendar_id=None, credentials=None, service=None):
    """Return calendar time zone from Google Service;
    Input:
        user_id - as it is in our database;
        calendar_id - as it is in Google Service; if not specified - use primary calendar;
    Output:
        time_zone - string - as it is in Google Service for the calendar;"""

    if not service:
        credentials = credentials or get_credentials(user_id)

    if not calendar_id:
        calendar_id = 'primary'

    service = service or get_calendar_sevice(user_id, credentials)
    result = service.calendarList().get(calendarId=calendar_id).execute()

    return result['timeZone']


def get_calendar_sevice(user_id, credentials=None):
    """Return calendar service;
    Input:
        user_id - as it is in our database;
        credentials - optional, if we already have credentials for the user;
    Output:
        service - Google Calendar service
    """
    credentials = credentials or get_credentials(user_id)

    try:
        service = build('calendar', 'v3', credentials=credentials)
    except AttributeError:
        logger.error(AttributeError, user_id=user_id)
        return None

    return service


def get_credentials(user_id):
    """Load credentials from our database and decode it;
    Input:
        user_id - as it is in our database;
    Output:
        credentials - dict - credentials for using GC service"""

    try:
        credentials = pickle.loads(get_user_settings(user_id).get('credentials'))

    except TypeError:
        logger.error(TypeError, user_id=user_id)
        credentials = None

    return credentials


def set_calendar_to_primary(user_id):
    """Set calendar id to primary value + restore time zone;
    Input:
        user_id - as it is in our database;
    Output:
        True/False - whether operation succeeded or not;"""

    try:
        time_zone = get_calendar_time_zone(user_id, calendar_id='primary')

        save_user(user_id, calendar_id='primary', time_zone=time_zone)

        return True

    except Exception as e:
        logger.exception(e, user_id=user_id)
        return False


def del_user(user_id):
    """Delete user from database;
    Input:
        user_id - as it is in our database;
    Output:
        True/False - whether operation succeeded or not;"""

    settings = connect_db()

    res = settings.settings.delete_one({'_id': {'$eq': user_id}})
    return res.deleted_count

def add_event(user_id, description, start, end, service=None, attendees=None, location=None):
    """Try to add event;
    Input:
        user_id - as it is in our database;
        description - string - main message for the event; first 50 symbols will be set as a title;
        start, end - datetime.datetime/ datetime.date - start and end time for an event
        service - Google Calendar service if already known
        attendees - [list of emails] - who will be invited to an event
        location - string - location for an event
    Output:
        ['CREATED', 'MISTAKE']
    """

    settings = get_user_settings(user_id)

    credentials = settings.get('credentials')
    time_zone = settings.get('time_zone')
    calendar_id = settings.get('calendar_id')

    if not calendar_id:
        set_calendar_to_primary(user_id)

    credentials = pickle.loads(credentials)

    start_formated, end_formated = get_formated_start_end_time(start, end, time_zone)

    event = {
        'start': start_formated,
        'end': end_formated,
        'summary': description[:50],
        'description': description,
        'location': location,
        'attendees': [{'email': email} for email in attendees] if attendees else None
    }

    service = service or get_calendar_sevice(user_id, credentials)

    try:
        service.events().insert(calendarId=calendar_id, body=event, sendNotifications=True).execute()
        return 'CREATED'

    except HttpError as err:
        logger.error(err, user_id=user_id)

        if err.resp.status == 404:
            pass

    return 'MISTAKE'

#Connect to the logger
logger = GCLogger()
