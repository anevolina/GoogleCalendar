"""Telegram Bot module for communicating with the main API"""

import os,sys,inspect
currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parentdir = os.path.dirname(currentdir)
sys.path.insert(0,parentdir)

import tg_bot.bot_answers as bot_answers
from core.main_api import (create_event, add_calendar, unbind_calendar, authorise_user_step1, authorise_user_step2,
    check_user_settings, logout)

from core.exceptions import GCUnauthorisedUserError

#settings - dict - auxiliary variable to store what kind of settings user is about to update
settings = {}


def handle_user_message(bot, update):
    """Handle simple message from user;
    Input:
        bot, update - dict - standart variables from telegram bot API
    Process:
        Check if we have user_id in settings variable - possible variants are ['CALENDAR', 'AUTHORISE'] - if the
        user want to change calendar or in the process of authorization.
        Else - parse the message and create an event;
    Output:
        message from bot to the user
    """

    user_id = get_user_id(bot, update)
    message = get_message(bot, update)

    user_set = get_settings(user_id, 'code')

    if user_set == 'CALENDAR':
        # if user wants to bind/add calendar to their account
        try:
            calendar_status = add_calendar(user_id=user_id, calendar_name=message)

        except GCUnauthorisedUserError:
            #if we don't have records about the user in database
            bot_answer = bot_answers.get_unauthorised_user_error_message()

        else:
            bot_answer = bot_answers.get_calendar_status_message(calendar_status, message)
            del_settings(user_id)

    elif user_set == 'AUTHORISE':
        #if user got auth url and now sent us the code
        authorised = authorise_user_step2(user_id, message)

        if authorised:
            bot_answer = bot_answers.get_authorised_message()
            message_id = update.message.message_id

            del_auth_messages(bot, user_id, message_id)
            del_settings(user_id)

        else:
            bot_answer = bot_answers.get_wrong_code_message()

    else:
        #assume user just wants to add an event
        try:
            status, start, attendees, location = create_event(user_id=user_id, message=message)

        except GCUnauthorisedUserError:
            # if we don't have records about the user in our database
            bot_answer = bot_answers.get_unauthorised_user_error_message()

        else:
            bot_answer = bot_answers.get_event_status_answer(status, start=start, attendees=attendees, location=location)

    send_message(bot, user_id, bot_answer)


def del_auth_messages(bot, user_id, message_id=None):
    """Delete two messages with auth url and user's code - just to be enough paranoid"""

    url_message = get_settings(user_id, 'url_message')

    if message_id:
        bot.delete_message(chat_id=user_id, message_id=message_id)

    if url_message:
        bot.delete_message(chat_id=user_id, message_id=url_message)

    pass


def add_calendar_callback(bot, update):
    """Reaction to /bind command - if we have records about the user in database, we will
    proceed and add 'CALENDAR' code to the settings variable"""

    user_id = get_user_id(bot, update)

    try:
        check_user_settings(user_id)

    except GCUnauthorisedUserError:
        # if we don't have records about the user in our database
        bot_answer = bot_answers.get_unauthorised_user_error_message()

    else:

        add_settings(user_id, code='CALENDAR')
        bot_answer = bot_answers.get_add_calendar_message()

    send_message(bot, user_id, bot_answer)


def chancel_callback(bot, update):
    """Reaction to /cancel command - cancel all started updates - regarding calendar setting or auth"""

    user_id = get_user_id(bot, update)

    del_auth_messages(bot, user_id)
    del_settings(user_id)

    bot_answer = bot_answers.get_canceled_message()
    send_message(bot, user_id, bot_answer)


def start_callback(bot, update):
    """Reaction to /start command - start auth process, and set 'AUTHORISE' code to the settings variable"""

    user_id = get_user_id(bot, update)

    url = authorise_user_step1()
    bot_answer = bot_answers.get_authorise_url_message(url)
    message = send_message(bot, user_id, bot_answer)
    add_settings(user_id, code='AUTHORISE', url_message=message.message_id)


def logout_callback(bot, update):
    """Reaction to /logout command - it delete all information about user from our database"""

    user_id = get_user_id(bot, update)

    try:
        status = logout(user_id=user_id)

    except GCUnauthorisedUserError:
        # if we don't have records about the user in our database
        bot_answer = bot_answers.get_unauthorised_user_error_message()

    else:
        bot_answer = bot_answers.get_logout_user_message(status)

    send_message(bot, user_id, bot_answer)


def help_callback(bot, update):
    """Reaction to /help command"""

    user_id = get_user_id(bot, update)
    bot_answer = bot_answers.get_help_message()
    send_message(bot, user_id, bot_answer)


def unbind_calendar_callback(bot, update):
    """Reaction to /unbind command - set calendar from customized to primary"""

    user_id = get_user_id(bot, update)

    try:
        status = unbind_calendar(user_id=user_id)

    except GCUnauthorisedUserError:
        # if we don't have records about the user in our database
        bot_answer = bot_answers.get_unauthorised_user_error_message()

    else:
        bot_answer = bot_answers.get_del_status_message(status)

    send_message(bot, user_id, bot_answer)


def add_settings(user_id, **kwargs):
    """Set settings for user in the settings variable with given kwargs"""

    settings[user_id] = {key: val for key, val in kwargs.items()}


def del_settings(user_id):
    """Delete user from the settings variable"""

    try:
        del settings[user_id]

    except KeyError:
        pass

    return


def get_settings(user_id, key=False):
    """Return value for the particular setting in the settings variable"""

    user_set = settings.get(user_id)

    if user_set and key:
        value = user_set.get(key)
        return value

    return user_set


def send_message(bot, chat_id, message):
    """Send message with telegram bot"""

    message = bot.send_message(chat_id=chat_id, text=message)
    return message


def get_user_id(bot, update):
    """Get user id from telegram bot update"""
    return update.message.from_user.id


def get_message(bot, update):
    """Get user message from telegram bot update"""
    return update.message.text.strip()