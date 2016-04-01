from __future__ import print_function()
from fabric.colors import red, green, yellow
import sys

def abort(message):
    print(red("FATAL: %s" % message), file=sys.stderr)
    sys.exit(1)


def error(message):
    print(red("ERROR: %s" % message), file=sys.stderr)


def warn(message):
    print(yellow("WARN: %s" % message), file=sys.stderr)


def info(message):
    print(green("INFO: %s" % message), file=sys.stderr)
