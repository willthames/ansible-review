from fabric.api import task, local, env, settings
from fabric.state import output
from fabric.colors import red, green, yellow
import sys
from ansiblereview.utils import abort, error, info, \
    warn, find_version, version_compare


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
    version = find_version(playbook)
    if not version:
        error("Playbook %s does not present version. "
              "Using latest standards" % playbook)
        version = standards.LATEST_STANDARD
    else:
        info("Playbook %s declares version %s" % (playbook, version))
    return version


@task(default=True)
def review(playbook):
    syntax_check(playbook)
    standard_version = find_version(playbook)
    for (version, standard) in standards.STANDARDS:
        result = standard.check(playbook)
        if result.failed:
            if version_compare(version, standard_version) < 0:
                warn("Future standard %s not met: %s" %
                     (standard.name, result.stderr))
            else:
                error("Declared standard %s not met: %s" %
                      (standard.name, result.stderr))


if __name__ == '__main__':
    sys.exit(review(sys.argv[1]))
