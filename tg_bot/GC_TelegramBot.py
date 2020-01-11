import tg_bot.bot_answers as bot_answers
from core.main_api import create_event, add_calendar, unbind_calendar, authorise_user_step1, authorise_user_step2

settings = {}
messages = {}

def handle_user_message(bot, update):
    user_id = get_user_id(bot, update)
    message = get_message(bot, update)

    user_set = get_settings(user_id, 'code')

    if user_set == 'CALENDAR':
        calendar_status = add_calendar(user_id, message)
        bot_answer = bot_answers.get_calendar_status_message(calendar_status, message)
        del_settings(user_id)

    elif user_set == 'AUTHORISE':
        authorised = authorise_user_step2(user_id, message)

        if authorised:
            bot_answer = bot_answers.get_authorised_message()
            message_id = update.message.message_id

            del_auth_messages(bot, user_id, message_id)
            del_settings(user_id)

        else:
            bot_answer = bot_answers.get_wrong_code_message()

    else:
        status, start, attendees, location = create_event(user_id, message)
        bot_answer = bot_answers.get_event_status_answer(status, start=start, attendees=attendees, location=location)

    send_message(bot, user_id, bot_answer)


def del_auth_messages(bot, user_id, message_id=None):
    url_message = get_settings(user_id, 'url_message')

    if message_id:
        bot.delete_message(chat_id=user_id, message_id=message_id)

    if url_message:
        bot.delete_message(chat_id=user_id, message_id=url_message)

    pass


def add_calendar_callback(bot, update):
    user_id = get_user_id(bot, update)
    add_settings(user_id, code='CALENDAR')

    bot_answer = bot_answers.get_add_calendar_message()
    send_message(bot, user_id, bot_answer)


def chancel_callback(bot, update):
    user_id = get_user_id(bot, update)

    del_auth_messages(bot, user_id)
    del_settings(user_id)

    bot_answer = bot_answers.get_canceled_message()
    send_message(bot, user_id, bot_answer)

def start_callback(bot, update):
    user_id = get_user_id(bot, update)

    url = authorise_user_step1(user_id)
    bot_answer = bot_answers.get_authorise_url_message(url)
    message = send_message(bot, user_id, bot_answer)
    add_settings(user_id, code='AUTHORISE', url_message=message.message_id)

def add_settings(user_id, **kwargs):
    settings[user_id] = {key: val for key, val in kwargs.items()}

def del_settings(user_id):
    try:
        del settings[user_id]
    except KeyError:
        pass

    return

def get_settings(user_id, key=False):
    user_set = settings.get(user_id)

    if user_set and key:
        key = user_set.get(key)
        return key

    return user_set


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
    message = bot.send_message(chat_id=chat_id, text=message)

    return message

def get_user_id(bot, update):
    return update.message.from_user.id

def get_message(bot, update):
    return update.message.text.strip()