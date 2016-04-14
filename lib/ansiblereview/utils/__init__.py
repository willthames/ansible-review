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


def lines_ranges(lines_spec):
    if not lines_spec:
        return None
    result = []
    for interval in lines_spec.split(","):
        (start, end) = interval.split("-")
        result.append(xrange(int(start), int(end)+1))
    return result


def is_line_in_ranges(line, ranges):
    return not ranges or any([line in r for r in ranges])


def review(candidate, settings, lines=None):
    errors = 0

    if not settings.rulesdir:
        abort("Standards directory is not set on command line or in configuration file - aborting")
    sys.path.append(os.path.expanduser(settings.rulesdir))
    try:
        standards = importlib.import_module('standards')
    except ImportError:
        abort("Could not find standards in directory %s" % settings.rulesdir)

    if not candidate.version:
        candidate.version = standards_latest(standards.standards)
        warn("%s %s does not present standards version. "
             "Using latest standards version %s" %
             (type(candidate).__name__, candidate.path, candidate.version))
    elif not settings.quiet:
        info("%s %s declares standards version %s" %
             (type(candidate).__name__, candidate.path, candidate.version))

    for standard in standards.standards:
        if type(candidate).__name__.lower() not in standard.types:
            continue
        result = standard.check(candidate, settings)
        for err in [err for err in result.errors
                      if is_line_in_ranges(err.lineno, lines_ranges(lines))]:
            if not standard.version or \
                    LooseVersion(standard.version) > LooseVersion(candidate.version):
                warn("Future standard \"%s\" not met:\n%s:%s" %
                     (standard.name, candidate.path, err))
            else:
                error("Standard \"%s\" not met:\n%s:%s" %
                      (standard.name, candidate.path, err))
                errors = errors + 1
        else:
            if not settings.quiet:
                if not standard.version:
                    info("Proposed standard \"%s\" met" % standard.name)
                else:
                    info("Standard \"%s\" met" % standard.name)

    return errors


class Settings(object):
    def __init__(self, values):
        self.rulesdir = values.get('rulesdir')
        self.lintdir = values.get('lintdir')
        self.quiet = values.get('quiet', False)


def read_config():
    config_dir = AppDirs("ansible-review", "com.github.willthames").user_config_dir
    config_file = os.path.join(config_dir, "config.ini")
    config = ConfigParser.RawConfigParser({'standards': None, 'lint': None})
    config.read(config_file)

    return Settings(dict(rulesdir=config.get('rules', 'standards'),
                         lintdir = config.get('rules', 'lint')))

