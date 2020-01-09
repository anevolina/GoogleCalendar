import bot_answers
from main_api import create_event, add_calendar, unbind_calendar, authorise, authosire_user_step1, authosire_user_step2

settings = {}

def handle_user_message(bot, update):
    user_id = get_user_id(bot, update)
    message = get_message(bot, update)

    user_set = settings.get(user_id)

    if user_set == 'CALENDAR':
        calendar_status = add_calendar(user_id, message)
        del settings[user_id]
        bot_answer = bot_answers.get_calendar_status_message(calendar_status, message)

    elif user_set == 'AUTHORISE':
        authorised = authosire_user_step2(user_id, message)
        if authorised:
            del settings[user_id]
            bot_answer = bot_answers.get_authorised_message()
        else:
            bot_answer = bot_answers.get_wrong_code_message()

    else:
        status, start, attendees, location = create_event(user_id, message)
        bot_answer = bot_answers.get_event_status_answer(status, start=start, attendees=attendees, location=location)

    send_message(bot, user_id, bot_answer)


def add_calendar_callback(bot, update):
    user_id = get_user_id(bot, update)
    settings[user_id] = 'CALENDAR'

    bot_answer = bot_answers.get_add_calendar_message()

    send_message(bot, user_id, bot_answer)


def chancel_callback(bot, update):
    user_id = get_user_id(bot, update)

    try:
        del settings[user_id]
    except KeyError:
        pass

    bot_answer = bot_answers.get_canceled_message()
    send_message(bot, user_id, bot_answer)

def start_callback(bot, update):
    user_id = get_user_id(bot, update)

    url = authosire_user_step1(user_id)

    bot_answer = bot_answers.get_authorise_url_message(url)
    send_message(bot, user_id, bot_answer)
    settings[user_id] = 'AUTHORISE'


def help_callback(bot, update):
    user_id = get_user_id(bot, update)
    bot_answer = bot_answers.get_help_message()
    send_message(bot, user_id, bot_answer)

def unbind_calendar_callback(bot, update):
    user_id = get_user_id(bot, update)

    status = unbind_calendar(user_id)
    bot_answer = bot_answers.get_del_status_message(status)

    send_message(bot, user_id, bot_answer)


def send_message(bot, chat_id, message):
    bot.send_message(chat_id=chat_id, text=message)

def get_user_id(bot, update):
    return update.message.from_user.id

def get_message(bot, update):
    return update.message.text.strip()