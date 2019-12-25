from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

import datetime
import pickle
import sqlite3

savings = None

def authorise(user_id):
    scopes = ['https://www.googleapis.com/auth/calendar']

    flow = InstalledAppFlow.from_client_secrets_file("client_secret.json", scopes=scopes)
    credentials = flow.run_console()

    save_user(user_id, credentials)

    return credentials

def connect_db():

    conn = None
    try:
        conn = sqlite3.connect('calendar_settings.sqlite')
    except:
        #Log connection error

        pass
    return conn

def save_user(user_id, credentials):

    service = get_calendar_sevice(user_id, credentials)

    time_zone = get_primary_time_zone(user_id, credentials=credentials, service=service)
    calendar_id = create_calendar(service, time_zone)
    credentials = pickle.dumps(credentials)
    param = (user_id, credentials, time_zone, calendar_id)

    insert_update_settings(param)


def insert_update_settings(param):

    settings = connect_db()
    sql = '''INSERT INTO settings (user_id, credentials, time_zone, calendar_id) VALUES (?, ?, ?, ?)
            ON CONFLICT(settings.user_id) DO UPDATE SET 
            credentials = excluded.credentials,
            time_zone = excluded.time_zone,
            calendar_id = excluded.calendar_id;'''

    settings.execute(sql, param)
    settings.commit()


def create_calendar(service, time_zone):
    calendar = {
        'summary': 'GCAPI Calendar',
        'timeZone': time_zone
    }

    created_calendar = service.calendars().insert(body=calendar).execute()

    return created_calendar['id']


def get_user_settings(user_id):

    settings = connect_db().cursor()

    sql = '''SELECT * FROM settings WHERE user_id=?'''
    result = settings.execute(sql, [user_id]).fetchone()

    if not result:
        authorise(user_id)
        result = get_user_settings(user_id)

    return result

def get_formated_start_end_time(start_time, end_time, time_zone):

    start = {'timeZone': time_zone}
    end = {'timeZone': time_zone}

    if isinstance(start_time, datetime.datetime):
        start['dateTime'] = start_time.strftime('%Y-%m-%dT%H:%M:%S')
        end['dateTime'] = end_time.strftime('%Y-%m-%dT%H:%M:%S')


    elif isinstance(start_time, datetime.date):
        start['date'] = start_time.strftime('%Y-%m-%d')
        end['date'] = end_time.strftime('%Y-%m-%d')

    return start, end

def get_primary_time_zone(user_id, credentials=None, service=None):

    service = service or get_calendar_sevice(user_id, credentials)
    result = service.calendarList().get(calendarId='primary').execute()

    return result['timeZone']

def get_calendar_sevice(user_id, credentials=None):

    credentials = credentials or authorise(user_id)
    service = build('calendar', 'v3', credentials=credentials)

    return service


def add_event(user_id, description, start, end, attendees=None, location=None):

    credentials, time_zone, calendar_id = get_user_settings(user_id)[1:4]
    credentials = pickle.loads(credentials)

    start, end = get_formated_start_end_time(start, end, time_zone)

    event = {
        'start': start,
        'end': end,
        'summary': description[:50],
        'description': description,
        'location': location,
        'attendees': [{'email': email} for email in attendees] if attendees else None
    }

    service = get_calendar_sevice(user_id, credentials)

    service.events().insert(calendarId=calendar_id, body=event, sendNotifications=True).execute()

    return