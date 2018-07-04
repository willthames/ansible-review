import logging

from ansiblereview.display.base import BaseDisplay

try:
    from ansible.utils.color import stringc
except ImportError:
    from ansible.color import stringc

 
class Display(BaseDisplay):

    def get_handler(self):
        logger = logging.getLogger(self.name)
        logger.setLevel(self.level)
        handler = logging.StreamHandler()
        handler.setLevel(self.level)
        handler.setFormatter(ColoredFormatter('%(message)s'))
        logger.addHandler(handler)
        return logger

class ColoredFormatter(logging.Formatter):
    def __init__(self, msg):
        logging.Formatter.__init__(self, msg)

    def format(self, record):
        levelname = record.levelname
        if levelname == logging.getLevelName(logging.WARNING):
            record.msg = stringc('WARN: %s' % record.msg, 'yellow')
        elif levelname == logging.getLevelName(logging.ERROR):
            record.msg = stringc('ERROR: %s' % record.msg, 'red')
        elif levelname == logging.getLevelName(logging.INFO):
            record.msg = stringc('INFO: %s' % record.msg, 'green')
        return logging.Formatter.format(self, record)
