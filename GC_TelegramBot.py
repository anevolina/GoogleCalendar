import bot_answers
from main_api import create_event, add_calendar

settings = {}

def handle_user_message(bot, update):
    user_id = get_user_id(bot, update)
    message = get_message(bot, update)

    if settings.get(user_id) == 'CALENDAR':
        calendar_status = add_calendar(user_id, message)
        bot_answer = bot_answers.get_calendar_status_message(calendar_status, message)

    else:
        status, start, attendees, location = create_event(user_id, message)
        bot_answer = bot_answers.get_event_status_answer(status, start=start, attendees=attendees, location=location)


def add_calendar_callback(bot, update):
    user_id = get_user_id(bot, update)
    settings[user_id] = 'CALENDAR'


def chancel_callback(bot, update):
    user_id = get_user_id(bot, update)

    try:
        del settings[user_id]
    except KeyError:
        pass


def get_user_id(bot, update):
    return update.message.from_user.id


def get_message(bot, update):
    return update.message.text.strip()

status, start, attendees, location = create_event(5, 'Test with attendees nasss@gmail.com 10 Jan 2020 at 15')
bot_answer = bot_answers.get_event_status_answer(status, start=start, attendees=attendees, location=location)

print(bot_answer)