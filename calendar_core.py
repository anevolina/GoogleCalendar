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

    save_credentials(user_id, credentials)

def make_connection(database):

    conn = None
    try:
        conn = sqlite3.connect(database)
    except:
        pass

def save_credentials(user_id, credentials):

    pickle.dump(credentials, open("token.pkl", "wb"))


def get_credentials():
    return pickle.load(open("token.pkl", "rb"))


def get_formated_start_end_time(start_time, end_time):

    time_zone = get_timezone()

    start = {'timeZone': time_zone}
    end = {'timeZone': time_zone}

    if isinstance(start_time, datetime.datetime):
        start['dateTime'] = start_time.strftime('%Y-%m-%dT%H:%M:%S')
        end['dateTime'] = end_time.strftime('%Y-%m-%dT%H:%M:%S')


    elif isinstance(start_time, datetime.date):
        start['date'] = start_time.strftime('%Y-%m-%d')
        end['date'] = end_time.strftime('%Y-%m-%d')

    return start, end

def get_timezone():

    service = get_calendar()
    result = service.calendarList().get(calendarId='primary').execute()

    return result['timeZone']

def get_calendar():
    credentials = get_credentials()
    service = build('calendar', 'v3', credentials=credentials)

    return service


def add_event(user_id, description, start, end, attendees=None, location=None):

    start, end = get_formated_start_end_time(start, end)

    event = {
        'start': start,
        'end': end,
        'summary': description[:50],
        'description': description,
        'location': location,
        'attendees': [{'email': email} for email in attendees] if attendees else None
    }

    service = get_calendar()

    service.events().insert(calendarId='primary', body=event, sendNotifications=True).execute()

    return

