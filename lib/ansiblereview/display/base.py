import logging


class BaseDisplay(object):

    def __init__(self, name, level=logging.ERROR):
        self.name = name
        self.level = level
        self.logger = self.get_handler()

    def get_handler(self):
        """ Returns a configured display or logging handler"""
        raise NotImplementedError()

    def info(self, msg, **kwargs):
        """ Handle info messages """
        raise NotImplementedError()

    def warn(self, msg, **kwargs):
        """ Handle warning messages """
        raise NotImplementedError()

    def error(self, msg, **kwargs):
        """ Handle error messages """
        raise NotImplementedError()
