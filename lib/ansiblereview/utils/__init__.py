from __future__ import print_function

import copy
import importlib
import logging
import os
import subprocess
import sys

from appdirs import AppDirs
from distutils.version import LooseVersion

import ansible
import ansiblereview
from ansiblereview.version import __version__
from ansiblereview.display import load_display_handler

import ansiblelint.version


try:
    import ConfigParser as configparser
except ImportError:
    import configparser


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
        raise SystemExit("Standards directory is not set on command line or in configuration "
                         "file - aborting")
    sys.path.append(os.path.abspath(os.path.expanduser(settings.rulesdir)))
    try:
        standards = importlib.import_module('standards')
    except ImportError as e:
        raise SystemExit("Could not import standards from directory %s: %s" %
                         (settings.rulesdir, str(e)))
    return standards


def review(candidate, settings, lines=None, display=None):
    errors = 0

    if not display:
        display = load_display_handler('default', __name__, logging.ERROR)

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
                display.warn("%s %s is in a role that contains a meta/main.yml without a declared "
                             "standards version. Using latest standards version %s" %
                             (type(candidate).__name__, candidate.path, candidate.version),
                             tag="standards_version", file=candidate.path)
            else:
                display.warn("%s %s does not present standards version. "
                             "Using latest standards version %s" %
                             (type(candidate).__name__, candidate.path, candidate.version),
                             tag="standards_version", file=candidate.path)

    display.info("%s %s declares standards version %s" %
                 (type(candidate).__name__, candidate.path, candidate.version),
                 tag="standards_version", file=candidate.path)

    for standard in standards.standards:
        if type(candidate).__name__.lower() not in standard.types:
            continue
        if settings.standards_filter and standard.name not in settings.standards_filter:
            continue
        result = standard.check(candidate, settings)
        labels = {'tag': 'review', 'standard': standard.name,
                  'file': candidate.path, 'passed': True}
        for err in [err for err in result.errors
                    if not err.lineno or
                    is_line_in_ranges(err.lineno, lines_ranges(lines))]:

            err_labels = copy.copy(labels)
            err_labels['passed'] = False
            if isinstance(err, ansiblereview.Error):
                err_labels.update(err.to_dict())

            if not standard.version:
                display.warn("Best practice \"%s\" not met:\n%s:%s" %
                             (standard.name, candidate.path, err), **err_labels)
            elif LooseVersion(standard.version) > LooseVersion(candidate.version):
                labels['practice'] = 'future'
                display.warn("Future standard \"%s\" not met:\n%s:%s" %
                             (standard.name, candidate.path, err), **err_labels)
            else:
                labels['practice'] = 'standard'
                display.error("Standard \"%s\" not met:\n%s:%s" %
                              (standard.name, candidate.path, err), **err_labels)
                errors = errors + 1
        if not result.errors:
            if not standard.version:
                labels['practice'] = 'best'
                display.info("Best practice \"%s\" met" % standard.name, **labels)
            elif LooseVersion(standard.version) > LooseVersion(candidate.version):
                labels['practice'] = 'future'
                display.info("Future standard \"%s\" met" % standard.name, **labels)
            else:
                labels['practice'] = 'standard'
                display.info("Standard \"%s\" met" % standard.name, **labels)

    return errors


class Settings(object):
    def __init__(self, values):
        self.rulesdir = values.get('rulesdir')
        self.lintdir = values.get('lintdir')
        self.configfile = values.get('configfile')


def read_config(config_file=None):
    if not config_file:
        config_file = get_default_config()
    config = configparser.RawConfigParser({'standards': None, 'lint': None})
    config.read(config_file)

    if config.has_section('rules'):
        return Settings(dict(rulesdir=config.get('rules', 'standards'),
                             lintdir=config.get('rules', 'lint'),
                             configfile=config_file))
    else:
        return Settings(dict(rulesdir=None, lintdir=None, configfile=config_file))


def get_default_config():
    config_dir = AppDirs("ansible-review", "com.github.willthames").user_config_dir
    return os.path.join(config_dir, "config.ini")


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
