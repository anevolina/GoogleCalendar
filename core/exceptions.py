class GCFlaskException(Exception):
    """
    Base exception
    """
    pass

class GCUnauthorisedUserError(GCFlaskException):
    """
    Error raised when we don't have credentials for current user (function get_user_settings returns None)
    to authorise they in Google Calendar service

    """
    pass