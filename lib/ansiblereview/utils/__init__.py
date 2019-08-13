from __future__ import print_function

try:
    from ansible.utils.color import stringc
except ImportError:
    from ansible.color import stringc
import ansiblereview
import ansible
from ansiblereview.version import __version__
import ansiblelint.version
from distutils.version import LooseVersion
import importlib
import logging
import os
import subprocess
import sys

try:
    import ConfigParser as configparser  # noqa
except ImportError:
    import configparser


def abort(message, file=sys.stderr):
    print(stringc("FATAL: %s" % message, 'red'), file=file)
    sys.exit(1)


def error(message, file=sys.stderr):
    print(stringc("ERROR: %s" % message, 'red'), file=file)


def warn(message, settings, file=sys.stdout):
    if settings.log_level <= logging.WARNING:
        print(stringc("WARN: %s" % message, 'yellow'), file=file)


def info(message, settings, file=sys.stdout):
    if settings.log_level <= logging.INFO:
        print(stringc("INFO: %s" % message, 'green'), file=file)


def standards_latest(standards):
    return max([standard.version for standard in standards if standard.version] or ["0.1"],
               key=LooseVersion)


def lines_ranges(lines_spec):
    if not lines_spec:
        return None
    result = []
    for interval in lines_spec.split(","):
        (start, end) = interval.split("-")
        result.append(range(int(start), int(end)+1))
    return result


def is_line_in_ranges(line, ranges):
    return not ranges or any([line in r for r in ranges])


def read_standards(settings):
    if not settings.rulesdir:
        abort("Standards directory is not set on command line or in configuration file - aborting")
    sys.path.append(os.path.abspath(os.path.expanduser(settings.rulesdir)))
    try:
        standards = importlib.import_module('standards')
    except ImportError as e:
        abort("Could not import standards from directory %s: %s" % (settings.rulesdir, str(e)))
    return standards


def review(candidate, settings, lines=None):
    errors = 0

    standards = read_standards(settings)
    if getattr(standards, 'ansible_min_version', None) and \
            LooseVersion(standards.ansible_min_version) > LooseVersion(ansible.__version__):
        raise SystemExit("Standards require ansible version %s (current version %s). "
                         "Please upgrade ansible." %
                         (standards.ansible_min_version, ansible.__version__))

    if getattr(standards, 'ansible_review_min_version', None) and \
            LooseVersion(standards.ansible_review_min_version) > LooseVersion(__version__):
        raise SystemExit("Standards require ansible-review version %s (current version %s). "
                         "Please upgrade ansible-review." %
                         (standards.ansible_review_min_version, __version__))

    if getattr(standards, 'ansible_lint_min_version', None) and \
            LooseVersion(standards.ansible_lint_min_version) > \
            LooseVersion(ansiblelint.version.__version__):
        raise SystemExit("Standards require ansible-lint version %s (current version %s). "
                         "Please upgrade ansible-lint." %
                         (standards.ansible_lint_min_version, ansiblelint.version.__version__))

    if not candidate.version:
        candidate.version = standards_latest(standards.standards)
        if candidate.expected_version:
            if isinstance(candidate, ansiblereview.RoleFile):
                if candidate.has_meta:
                    warn("%s %s is in a role that contains a meta/main.yml without a declared "
                         "standards version. "
                         "Using latest standards version %s" %
                         (type(candidate).__name__, candidate.path, candidate.version),
                         settings)
            else:
                warn("%s %s does not present standards version. "
                     "Using latest standards version %s" %
                     (type(candidate).__name__, candidate.path, candidate.version),
                     settings)

    info("%s %s declares standards version %s" %
         (type(candidate).__name__, candidate.path, candidate.version),
         settings)

    for standard in standards.standards:
        if type(candidate).__name__.lower() not in standard.types:
            continue
        if settings.standards_filter and standard.name not in settings.standards_filter:
            continue
        result = standard.check(candidate, settings)
        for err in [err for err in result.errors
                    if not err.lineno or
                    is_line_in_ranges(err.lineno, lines_ranges(lines))]:
            if not standard.version:
                warn("Best practice \"%s\" not met:\n%s:%s" %
                     (standard.name, candidate.path, err), settings)
            elif LooseVersion(standard.version) > LooseVersion(candidate.version):
                warn("Future standard \"%s\" not met:\n%s:%s" %
                     (standard.name, candidate.path, err), settings)
            else:
                error("Standard \"%s\" not met:\n%s:%s" %
                      (standard.name, candidate.path, err))
                errors = errors + 1
        if not result.errors:
            if not standard.version:
                info("Best practice \"%s\" met" % standard.name, settings)
            elif LooseVersion(standard.version) > LooseVersion(candidate.version):
                info("Future standard \"%s\" met" % standard.name, settings)
            else:
                info("Standard \"%s\" met" % standard.name, settings)

    return errors


class Settings(object):
    def __init__(self, values):
        self.rulesdir = values.get('rulesdir')
        self.lintdir = values.get('lintdir')
        self.configfile = values.get('configfile')
        self.indent_list_items = values.get('indent_list_items')


def read_config(config_file):
    config = configparser.RawConfigParser(dict(standards=None, lint=None, indent_list_items=False))
    config.read(config_file)

    if config.has_section('rules'):
        return Settings(
                dict(rulesdir=config.get('rules', 'standards'),
                     lintdir=config.get('rules', 'lint'),
                     configfile=config_file,
                     indent_list_items=config.getboolean('rules', 'indent_list_items')
                     ))
    else:
        return Settings(dict(rulesdir=None, lintdir=None,
                             configfile=config_file, indent_list_items=False))


class ExecuteResult(object):
    pass


def execute(cmd):
    result = ExecuteResult()
    encoding = 'UTF-8'
    env = dict(os.environ)
    env['PYTHONIOENCODING'] = encoding
    proc = subprocess.Popen(cmd, stdout=subprocess.PIPE,
                            stderr=subprocess.STDOUT, env=env)
    result.output = proc.communicate()[0].decode(encoding)
    result.rc = proc.returncode
    return result
