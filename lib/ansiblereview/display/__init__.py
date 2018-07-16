import logging
import importlib

DISPLAY_NAMES = [
    'default',
    'json'
]


def load_display_handler(handler_name, name, level=logging.ERROR):
    mod = importlib.import_module('.display.%s' % handler_name, package='ansiblereview')
    return mod.Display(name, level=level)
