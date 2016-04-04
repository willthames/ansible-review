from __future__ import print_function
from fabric.colors import red, green, yellow
import re
import sys
from distutils.version import LooseVersion

def abort(message):
    print(red("FATAL: %s" % message), file=sys.stderr)
    sys.exit(1)


def error(message):
    print(red("ERROR: %s" % message), file=sys.stderr)


def warn(message):
    print(yellow("WARN: %s" % message), file=sys.stderr)


def info(message):
    print(green("INFO: %s" % message), file=sys.stderr)


def find_version(filename, version_regex="^# Standards: \([0-9]+(\.[0-9])+\)"):
    version_re = re.compile(version_regex)
    with open(filename, 'r') as f:
        for line in f:
            match = version_re.match(line)
            if match:
                return match.group(0)
    return None


def standards_latest(standards):
    return max([standard.version for standard in standards], key=LooseVersion)
