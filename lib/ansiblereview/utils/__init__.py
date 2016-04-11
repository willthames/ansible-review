from __future__ import print_function
from fabric.colors import red, green, yellow
import importlib
import os
import sys
from distutils.version import LooseVersion
from appdirs import AppDirs
import ConfigParser


def abort(message):
    print(red("FATAL: %s" % message), file=sys.stderr)
    sys.exit(1)


def error(message):
    print(red("ERROR: %s" % message), file=sys.stderr)


def warn(message):
    print(yellow("WARN: %s" % message))


def info(message):
    print(green("INFO: %s" % message))


def standards_latest(standards):
    return max([standard.version for standard in standards if standard.version], key=LooseVersion)


def review(candidate, settings):
    errors = 0

    sys.path.append(os.path.expanduser(settings.rulesdir))
    standards = importlib.import_module('standards')

    if not candidate.version:
        candidate.version = standards_latest(standards.standards)
        warn("%s %s does not present standards version. "
             "Using latest standards version %s" %
             (type(candidate).__name__, candidate.path, candidate.version))
    else:
        info("%s %s declares standards version %s" %
             (type(candidate).__name__, candidate.path, candidate.version))

    for standard in standards.standards:
        if type(candidate).__name__.lower() not in standard.types:
            continue
        result = standard.check(candidate, settings)
        if result.failed:
            if not standard.version or \
                    LooseVersion(standard.version) > LooseVersion(candidate.version):
                warn("Future standard \"%s\" not met:\n%s" %
                     (standard.name, result.stdout + result.stderr))
            else:
                error("Standard \"%s\" not met:\n%s" %
                      (standard.name, result.stdout + result.stderr))
                errors = errors + 1
        else:
            if not standard.version:
                info("Proposed standard \"%s\" met" % standard.name)
            else:
                info("Standard \"%s\" met" % standard.name)

    return errors


class Settings(object):
    def __init__(self, values):
        self.rulesdir = values.get('rulesdir')
        self.lintdir = values.get('lintdir')


def read_config():
    config_dir = AppDirs("ansible-review", "com.github.willthames").user_config_dir
    config_file = os.path.join(config_dir, "config.ini")
    config = ConfigParser.RawConfigParser({'standards': None, 'lint': None})
    config.read(config_file)

    return Settings(dict(rulesdir=config.get('rules', 'standards'),
                         lintdir = config.get('rules', 'lint')))

