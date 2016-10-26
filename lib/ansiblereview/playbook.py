from ansiblereview import utils, Playbook, Result, Error
from ansiblelint.utils import parse_yaml_linenumbers, get_action_tasks
import codecs
from collections import defaultdict
import os


def install_roles(playbook, settings):
    rolesdir = os.path.join(os.path.dirname(playbook), "roles")
    rolesfile = os.path.join(os.path.dirname(playbook), "rolesfile.yml")
    if not os.path.exists(rolesfile):
        rolesfile = os.path.join(os.path.dirname(playbook), "rolesfile")
    if os.path.exists(rolesfile):
        utils.info("Installing roles: Using rolesfile %s and roles dir %s" % (rolesfile, rolesdir),
                   settings)
        result = utils.execute(["ansible-galaxy", "install", "-r", rolesfile, "-p", rolesdir])
        if result.rc:
            utils.error("Could not install roles from %s:\n%s" %
                        (rolesdir, result.output))
        else:
            utils.info(u"Roles installed \u2713", settings)
    else:
        utils.warn("No roles file found for playbook %s, tried %s and %s.yml" %
                   (playbook, rolesfile, rolesfile), settings)


def syntax_check(playbook, settings):
    result = utils.execute(["ansible-playbook", "--syntax-check", playbook])
    if result.rc:
        message = "FATAL: Playbook syntax check failed for %s:\n%s" % \
            (playbook, result.output)
        utils.abort(message)
    else:
        utils.info("Playbook syntax check succeeded for %s" % playbook, settings)


def review(playbook, settings):
    install_roles(playbook, settings)
    syntax_check(playbook, settings)
    return utils.review(Playbook(playbook), settings)


def repeated_names(playbook, settings):
    with codecs.open(playbook['path'], mode='rb', encoding='utf-8') as f:
        yaml = parse_yaml_linenumbers(f, playbook['path'])
    namelines = defaultdict(list)
    errors = []
    if yaml:
        for task in get_action_tasks(yaml, playbook):
            if 'name' in task:
                namelines[task['name']].append(task['__line__'])
        for (name, lines) in namelines.items():
            if len(lines) > 1:
                errors.append(Error(lines[-1],
                                    "Task/handler name %s appears multiple times" % name))
    return Result(playbook, errors)
