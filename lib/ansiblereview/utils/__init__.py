from __future__ import print_function

try:
    from ansible.utils.color import stringc
except ImportError:
    from ansible.color import stringc
import ansiblereview
from appdirs import AppDirs
import ConfigParser
from distutils.version import LooseVersion
import importlib
import os
import subprocess
import sys


def abort(message, file=sys.stderr):
    print(stringc("FATAL: %s" % message, 'red'), file=file)
    sys.exit(1)


def error(message, file=sys.stderr):
    print(stringc("ERROR: %s" % message, 'red'), file=file)


def warn(message, file=sys.stdout):
    print(stringc("WARN: %s" % message, 'yellow'), file=file)


def info(message, file=sys.stdout):
    print(stringc("INFO: %s" % message, 'green'), file=file)


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
    sys.path.append(os.path.abspath(os.path.expanduser(settings.rulesdir)))
    try:
        standards = importlib.import_module('standards')
    except ImportError:
        abort("Could not find standards in directory %s" % settings.rulesdir)

    if not candidate.version:
        candidate.version = standards_latest(standards.standards)
        if isinstance(candidate, ansiblereview.RoleFile):
            warn("%s %s is in a role that contains a meta/main.yml without a declared "
                 "standards version. "
                 "Using latest standards version %s" %
                 (type(candidate).__name__, candidate.path, candidate.version))
        else:
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
        if not result.errors:
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
        self.configfile = values.get('configfile')
        self.quiet = values.get('quiet', False)


def read_config():
    config_dir = AppDirs("ansible-review", "com.github.willthames").user_config_dir
    config_file = os.path.join(config_dir, "config.ini")
    config = ConfigParser.RawConfigParser({'standards': None, 'lint': None})
    config.read(config_file)

    if config.has_section('rules'):
        return Settings(dict(rulesdir=config.get('rules', 'standards'),
                             lintdir=config.get('rules', 'lint'),
                             configfile=config_file))
    else:
        return Settings(dict(rulesdir=None, lintdir=None, configfile=config_file))


class ExecuteResult(object):
    pass


def execute(cmd):
    result = ExecuteResult()
    try:
        result.output = subprocess.check_output(cmd, stderr=subprocess.STDOUT)
        result.rc = 0
    except subprocess.CalledProcessError, e:
        result.rc = e.returncode
        result.output = e.output
    return result
