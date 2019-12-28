from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

import datetime
import pickle
import sqlite3


def authorise(user_id):
    scopes = ['https://www.googleapis.com/auth/calendar']

    flow = InstalledAppFlow.from_client_secrets_file("client_secret.json", scopes=scopes)
    credentials = flow.run_console()

    save_user(user_id, credentials=credentials)

    return credentials

def connect_db():

    conn = None
    try:
        conn = sqlite3.connect('calendar_settings.sqlite')
    except:
        #Log connection error

        pass
    return conn


def save_user(user_id, **kwargs):

    settings = connect_db()

    if 'credentials' in kwargs.keys():
        save_credentials(settings, user_id, kwargs['credentials'])
        del kwargs['credentials']

    if kwargs.keys():
        save_settings(settings, user_id, **kwargs)

    settings.commit()


def save_credentials(settings, user_id, credentials):
    credentials = pickle.dumps(credentials)

    sql = """INSERT INTO settings (user_id, credentials) VALUES (? ,?)
            ON CONFLICT(settings.user_id) DO UPDATE SET
            credentials = excluded.credentials"""

    settings.execute(sql, (user_id, credentials))


def save_settings(settings, user_id, **kwargs):

    on_update = get_update_sql_text(**kwargs)
    columns, values = get_insert_sql_text(**kwargs)

    sql = '''INSERT INTO settings (user_id, {columns}) VALUES ({user_id},{values})
            ON CONFLICT(settings.user_id) DO UPDATE SET 
            {on_update};'''.format(columns=columns, user_id=user_id, values=values, on_update=on_update)

    settings.execute(sql)


def get_update_sql_text(**kwargs):
     on_update = ',\n'.join(key + ' = excluded.' + key for key in kwargs.keys())

     return on_update


def get_insert_sql_text(**kwargs):
    columns = ','.join(key for key in kwargs.keys())
    values = ','.join("\"" + value + "\"" for value in kwargs.values())

    return columns, values


def create_calendar(user_id, calendar_name, service=None):

    credentials, time_zone = get_user_settings(user_id)[1:3]
    credentials = pickle.loads(credentials)

    service = service or get_calendar_sevice(user_id, credentials=credentials)

    if not time_zone:
        time_zone = get_primary_time_zone(user_id, service=service)

    calendar = {
        'summary': calendar_name,
        'timeZone': time_zone
    }

    created_calendar = service.calendars().insert(body=calendar).execute()

    calendar_id = created_calendar['id']

    save_user(user_id, calendar_id=calendar_id)

    return


def get_user_settings(user_id):

    settings = connect_db().cursor()

    sql = '''SELECT * FROM settings WHERE user_id=?'''
    result = settings.execute(sql, [user_id]).fetchone()

    if not result:
        authorise(user_id)
        return get_user_settings(user_id)

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

    if not service:
        credentials = credentials or get_user_settings(user_id)[1]

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

