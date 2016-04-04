from fabric.api import task, local, env, settings
from fabric.state import output

from ansiblereview import utils
from ansiblereview.version import __version__

from distutils.version import LooseVersion
import importlib
import optparse
import os
import sys


env.colorize_errors = True
output.warnings = False
output.running = False
env.warn_only = True


@task
def install_roles(playbook):

    rolesdir = os.path.join(os.path.dirname(playbook), "roles")
    rolesfile = os.path.join(os.path.dirname(playbook), "rolesfile.yml")
    if not os.path.exists(rolesfile):
        rolesfile = os.path.join(os.path.dirname(playbook), "rolesfile")
    if os.path.exists(rolesfile):
        utils.info("Installing roles: Using rolesfile %s and roles dir %s" % (rolesfile, rolesdir))
        result = local("ansible-galaxy install -r %s -p %s -f" %
               (rolesfile, rolesdir), capture=True)
        utils.info(u"Roles installed \u2713")
        if result.failed:
            utils.error("Could not install roles from %s:\n%s" %
                   (rolesdir, result.stderr))
    else:
        utils.warn("No roles file found for playbook %s, tried %s and %s.yml" %
               (playbook, rolesfile, rolesfile))


@task
def syntax_check(playbook):
    result = local("ansible-playbook --syntax-check %s" % playbook, capture=False)
    if result.failed:
        message = "FATAL: Playbook syntax check failed for %s:\n%s" % \
            (playbook, result.stderr)
        utils.abort(message)
    else:
        utils.info("Playbook syntax check succeeded for %s" % playbook)


@task
def find_version(playbook):
    version = utils.find_version(playbook)
    return version


@task(default=True)
def review(playbook, settings):
    #install_roles(playbook)
    errors = False
    syntax_check(playbook)
    playbook_version = utils.find_version(playbook)

    sys.path.append(settings.directory)
    standards = importlib.import_module('standards')

    if not playbook_version:
        playbook_version = utils.standards_latest(standards.standards)
        utils.error("Playbook %s does not present standards version. "
              "Using latest standards version %s" %
              (playbook, playbook_version))
        errors = True
    else:
        utils.info("Playbook %s declares standards version %s" %
                (playbook, playbook_version))

    for standard in standards.standards:
        if "playbook" not in standard.types:
            continue
        result = standard.check(playbook, settings)
        if result.failed:
            if LooseVersion(standard.version) < LooseVersion(playbook_version):
                utils.warn("Future standard \"%s\" not met:\n%s" %
                     (standard.name, result.stderr))
            else:
                utils.error("Declared standard \"%s\" not met:\n%s" %
                      (standard.name, result.stderr))
                errors = True
    return int(errors)


if __name__ == '__main__':
    parser = optparse.OptionParser("%prog playbook.yml",
                                    version="%prog " + __version__)
    parser.add_option('-d', dest='directory',
            help="Location of standards rules")
    parser.add_option('-r', dest='rulesdir',
            help="Location of additional lint rules")
    options, args = parser.parse_args(sys.argv)
    sys.exit(review(args[1], options))
