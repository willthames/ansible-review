from fabric.api import task, local, env, settings
from fabric.state import output

import ansiblereview.utils

import sys
import optparse
from distutils.version import LooseVersion


env.colorize_errors = True
output.warnings = False
env.warn_only = True


@task
def syntax_check(playbook):
    result = local("ansible-playbook --syntax-check %s" % playbook)
    if result.failed:
        message = "FATAL: Playbook syntax check failed on %s" % playbook
        abort(message)


@task
def find_version(playbook):
    version = utils.find_version(playbook)
    return version


@task(default=True)
def review(playbook, config):
    syntax_check(playbook)
    standard_version = utils.find_version(playbook)

    sys.path.append(config.directory)
    importlib.import_module('standards')

    if not playbook_version:
        playbook_version = utils.standards_latest(standards)
        utils.error("Playbook %s does not present standards version. "
              "Using latest standards version %s" %
              (playbook, playbook_version))
    else:
        utils.info("Playbook %s declares standards version %s" %
                (playbook, playbook_version))

    for standard in standards:
        if "playbook" not in standard.types:
            continue
        result = standard.check(playbook)
        if result.failed:
            if LooseVersion(standard.version) < LooseVersion(playbook_version):
                utils.warn("Future standard %s not met: %s" %
                     (standard.name, result.stderr))
            else:
                utils.error("Declared standard %s not met: %s" %
                      (standard.name, result.stderr))


if __name__ == '__main__':
    parser = optparse.OptionParser("%prog playbook.yml",
                                    version="%prog " + __version__)
    parser.add_option('-d', dest='directory',
            help="Location of standards rules")
    options, args = parser.parse_args(args)
    sys.exit(review(args[1], options))
