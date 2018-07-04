import logging


class BaseDisplay(object):

    def __init__(self, name, level=logging.ERROR):
        self.name = name
        self.level = level

    def get_handler(self):
        """ Returns a configured display or logging handler"""
        raise NotImplementedError()
