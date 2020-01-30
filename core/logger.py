"""Settings for project logger"""

import logging

class GCLogger():

    def __init__(self):
        """Define logging parameters: level, file, format for messages"""

        self.logger = logging.getLogger('GCAddEvent')
        self.logger.setLevel(logging.INFO)

        fh = logging.FileHandler('GCAddEvent.log')

        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        fh.setFormatter(formatter)

        self.logger.addHandler(fh)

    def info(self, *args, **kwargs):
        """Define logging for info events"""

        message = self.get_message(*args, **kwargs)
        self.logger.info(message)

    def exception(self, *args, **kwargs):
        """Define logging for exceptions"""

        message = self.get_message(*args, **kwargs)
        self.logger.exception(message)

    def error(self, *args, **kwargs):
        """Define logging for errors"""

        message = self.get_message(*args, **kwargs)
        self.logger.error(message)


    def get_message(self, *args, **kwargs):
        """Assemble message from given args and kwargs"""

        message = ''
        message += ', '.join([str(key) + ': ' + str(val) for key, val in kwargs.items()]) + '; ' if kwargs else ''
        message += ', '.join(str(val) for val in args) if args else ''

        return message