import datetime
import pickle
import sqlite3
import os

from google_auth_oauthlib.flow import Flow, InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError


def authorise(user_id):
    scopes = ['https://www.googleapis.com/auth/calendar']

    flow = InstalledAppFlow.from_client_secrets_file("client_secret.json", scopes=scopes)
    credentials = flow.run_console()

    save_user(user_id, credentials=pickle.dumps(credentials))

    return credentials

def get_authorisation_url():
    flow = get_flow()
    auth_url, _ = flow.authorization_url(prompt='consent')

    return auth_url

def fetch_token(user_id, code):

    flow = get_flow()

    try:
        flow.fetch_token(code=code)
        credentials = flow.credentials
        save_user(user_id, credentials=pickle.dumps(credentials))
        return True
    except Exception as e:
        print(e)
        #Log error

        return False

def get_flow():
    scopes = ['https://www.googleapis.com/auth/calendar']

    client_secret = get_path('client_secret.json')

    flow = Flow.from_client_secrets_file(
        client_secret,
        scopes=scopes,
        redirect_uri='urn:ietf:wg:oauth:2.0:oob')

    return flow

def get_path(file_name):

    path = os.path.dirname(os.path.abspath(__file__))
    file_name = os.path.join(path, file_name)

    return file_name

def connect_db():

    conn = None
    try:
        db_path = get_path('calendar_settings.sqlite')
        conn = sqlite3.connect(db_path)
    except:
        #Log connection error

        pass
    return conn


def save_user(user_id, **kwargs):

    settings = connect_db()
    save_settings(settings, user_id, **kwargs)
    settings.commit()


def save_settings(settings, user_id, **kwargs):

    on_update = get_update_sql_text(**kwargs)
    columns, values = get_insert_sql_text(**kwargs)

    sql = '''INSERT INTO settings (user_id, {columns}) VALUES ({user_id},{values})
            ON CONFLICT(settings.user_id) DO UPDATE SET 
            {on_update};'''.format(columns=columns, user_id=user_id, values=values, on_update=on_update)

    param = tuple(kwargs.values())
    settings.execute(sql, param)


def get_update_sql_text(**kwargs):
     on_update = ',\n'.join(key + ' = excluded.' + key for key in kwargs.keys())

     return on_update


def get_insert_sql_text(**kwargs):
    columns = ','.join(key for key in kwargs.keys())
    values = ','.join('?' for _ in range(len(kwargs.values())))

    return columns, values


def create_calendar(user_id, calendar_name, service=None):

    credentials, time_zone = get_user_settings(user_id)[1:3]
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
        #Log error
        calendar_id = None

    return calendar_id is not None


def fetch_calendar(user_id, calendar_name):

    calendar_id = get_calendar_id(user_id, calendar_name)
    time_zone = get_calendar_time_zone(user_id, calendar_id=calendar_id)

    save_user(user_id, calendar_id=calendar_id, time_zone=time_zone)

    return calendar_id is not None


def get_calendar_id(user_id, calendar_name):
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

def get_calendar_time_zone(user_id, calendar_id=None, credentials=None, service=None):

    if not service:
        credentials = credentials or get_credentials(user_id)

    if not calendar_id:
        calendar_id = 'primary'

    service = service or get_calendar_sevice(user_id, credentials)
    result = service.calendarList().get(calendarId=calendar_id).execute()

    return result['timeZone']

def get_calendar_sevice(user_id, credentials=None):

    credentials = credentials or get_credentials(user_id)

    try:
        service = build('calendar', 'v3', credentials=credentials)

    except AttributeError:
        authorise(user_id)
        return get_calendar_sevice(user_id)

    return service

def  get_credentials(user_id):

    credentials = pickle.loads(get_user_settings(user_id)[1])

    if not credentials:
        credentials = authorise(user_id)

    return credentials

def set_calendar_to_primary(user_id):

    try:

        time_zone = get_calendar_time_zone(user_id)
        save_user(user_id, calendar_id='primary', time_zone=time_zone)

        return True

    except:

        return False



def add_event(user_id, description, start, end, service=None, attendees=None, location=None):

    credentials, time_zone, calendar_id = get_user_settings(user_id)[1:4]
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
        # log calendar_id not found... or something else wrong
        if err.resp.status == 404:
            save_user(user_id, calendar_id='primary')
            add_event(user_id, description, start, end, service=service, attendees=attendees, location=location, )

    return 'MISTAKE'