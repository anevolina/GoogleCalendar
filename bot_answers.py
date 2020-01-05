def get_calendar_status_message(status, message):
    if status == 'FETCHED':
        message = 'Calendar ' + message + 'was added to your account.'

    elif status == 'CREATED':
        message = 'Calendar ' + message + 'was created.'

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