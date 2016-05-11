from collections import defaultdict

from ansiblereview import utils, Playbook, Result, Error
import ansiblelint

import os


def install_roles(playbook):

    rolesdir = os.path.join(os.path.dirname(playbook), "roles")
    rolesfile = os.path.join(os.path.dirname(playbook), "rolesfile.yml")
    if not os.path.exists(rolesfile):
        rolesfile = os.path.join(os.path.dirname(playbook), "rolesfile")
    if os.path.exists(rolesfile):
        utils.info("Installing roles: Using rolesfile %s and roles dir %s" % (rolesfile, rolesdir))
        result = utils.execute(["ansible-galaxy", "install", "-r", rolesfile, "-p", rolesdir])
        if result.rc:
            utils.error("Could not install roles from %s:\n%s" %
                        (rolesdir, result.output))
        else:
            utils.info(u"Roles installed \u2713")
    else:
        utils.warn("No roles file found for playbook %s, tried %s and %s.yml" %
                   (playbook, rolesfile, rolesfile))


def syntax_check(playbook):
    result = utils.execute(["ansible-playbook", "--syntax-check", playbook])
    if result.rc:
        message = "FATAL: Playbook syntax check failed for %s:\n%s" % \
            (playbook, result.output)
        utils.abort(message)
    else:
        utils.info("Playbook syntax check succeeded for %s" % playbook)


def review(playbook, settings):
    install_roles(playbook)
    syntax_check(playbook)
    return utils.review(Playbook(playbook), settings)


def repeated_names(playbook, settings):
    yaml = ansiblelint.utils.parse_yaml_linenumbers(playbook.path)
    namelines = defaultdict(list)
    errors = []
    if yaml:
        for task in ansiblelint.utils.get_action_tasks(yaml, playbook):
            if 'name' in task:
                namelines['name'].append(task['__line__'])
        for (name, lines) in namelines.items():
            if len(lines) > 1:
                errors.append(Error(lines[-1], "Task/handler name %s appears multiple times" % name))
    return Result(playbook, errors)
