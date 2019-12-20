from calendar_core import add_event
import datefinder
import datetime
import re

def create_event(user_id, message):

    attendees = find_attendees(message)
    location = find_location(message)
    start, end = get_start_end_time(message)

    add_event(user_id, message, start, end, attendees=attendees, location=location)


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

message = """"""

create_event(1, message)