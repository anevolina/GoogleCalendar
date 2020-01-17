def get_calendar_status_message(status, message):
    if status == 'FETCHED':
        message = 'Calendar ' + message + ' was bind with your account'

    elif status == 'CREATED':
        message = 'Calendar ' + message + ' was created'

    else:
        message = 'Something went wrong. Please, try again'

    return message


def get_event_status_answer(status, start, **kwargs):

    if status == 'CREATED':
        message = 'Event started from {} was added.'.format(start.strftime("%d %B %Y, %H:%M:%S"))
        if kwargs.get('location'):
            message += '\nEvent location: ' + kwargs['location']
        if kwargs.get('attendees'):
            message += '\nInvited guests: ' + ', '.join(kwargs['attendees'])

    else:
        message = 'Something went wrong. Please, try again'

    return message

def get_add_calendar_message():
    message = 'Give me exact name of an existed calendar, connected to your account, or any other name to create a new ' \
              'calendar\n\n' \
              '/cancel to cancel this action'

    return message

def get_canceled_message():
    message = 'Operation canceled'

    return message

def get_help_message():
    message = 'To start, type a message... Write here something else, please.\n\n' \
              '/bind - to customise in which calendar I will save all events\n' \
              '/unbind - to set the calendar to the default value\n' \
              '/start - to authorise with new email\n' \
              '/logout - to logout from Google Calendar service for this bot'

    return message

def get_authorise_url_message(url):
    message = 'Please, get a validation code following instructions from this url so I could add ' \
              'calendars and events to your account\n\n' + url + \
                '\n\n/cancel to cancel this action'

    return message


def get_del_status_message(status):

    if status:
        message = 'Calendar was set to the default value (primary calendar for your email)'

    else:
        message = 'Something went wrong. Please, try again'

    return message

def get_authorised_message():
    message = 'Access granted. Now you can add events through this bot.\n\n' + get_help_message()

    return message

def get_wrong_code_message():
    message = 'Something went wrong. Make sure you paste the whole code for authorisation.\n' \
              '/cancel to cancel this operation'

    return message

def get_unauthorised_user_error_message():

    message = 'You didn\'t authorise at Google Calendar service.\n\n' \
                      'Press /start to connect'

    return message

def get_logout_user_message(status):
    if status:
        message = 'You\'ve been logout from Google Calendar service'
    else:
        message = 'Something went wrong, please try again later'
    return message