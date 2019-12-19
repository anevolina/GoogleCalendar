from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

import datetime
import pickle
import datefinder


def authorise():
    scopes = ['https://www.googleapis.com/auth/calendar']

    flow = InstalledAppFlow.from_client_secrets_file("client_secret.json", scopes=scopes)
    credentials = flow.run_console()

    dump_credentials(credentials)


def dump_credentials(credentials):
    pickle.dump(credentials, open("token.pkl", "wb"))


def get_credentials():
    return pickle.load(open("token.pkl", "rb"))


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


def get_formated_start_end_time(start_time: str, duration=1):

    time_zone = get_timezone()

    start_time, end_time = get_start_end_time(start_time, duration)

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


def add_event(start_time, summary, duration=1, attendees=None, description=None, location=None):

    start, end = get_formated_start_end_time(start_time, duration)

    event = {
        'start': start,
        'end': end,
        'summary': summary,
        'description': description,
        'location': location,
        'attendees': [{'email': email} for email in attendees] if attendees else None
    }

    service = get_calendar()

    service.events().insert(calendarId='primary', body=event, sendNotifications=True).execute()

    return


add_event('завтра', 'test summary', description='Test description')

