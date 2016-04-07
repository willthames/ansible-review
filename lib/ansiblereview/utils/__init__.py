from __future__ import print_function
from fabric.colors import red, green, yellow
import importlib
import os
import sys
from distutils.version import LooseVersion


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
    errors = False

    sys.path.append(os.path.expanduser(settings.rulesdir))
    standards = importlib.import_module('standards')

    if not candidate.version:
        candidate.version = standards_latest(standards.standards)
        error("%s %s does not present standards version. "
              "Using latest standards version %s" %
              (type(candidate).__name__, candidate.path, candidate.version))
        errors = True
    else:
        info("%s %s declares standards version %s" %
             (type(candidate).__name__, candidate.path, candidate.version))

    for standard in standards.standards:
        if type(candidate).__name__.lower() not in standard.types:
            continue
        result = standard.check(candidate.path, settings)
        if result.failed:
            if not standard.version or \
                    LooseVersion(standard.version) > LooseVersion(candidate.version):
                warn("Future standard \"%s\" not met:\n%s" %
                     (standard.name, '\n'.join([result.stdout, result.stderr])))
            else:
                error("Standard \"%s\" not met:\n%s" %
                      (standard.name, '\n'.join([result.stdout, result.stderr])))
                errors = True
        else:
            if not standard.version:
                info("Proposed standard \"%s\" met" % standard.name)
            else:
                info("Standard \"%s\" met" % standard.name)


    return int(errors)
