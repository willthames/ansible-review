# This is an example standards file (based on real needs)
# Playbooks and meta/main.yml files are expected (but not
# required) to declare a standards version. Typically you
# will add new standards at a particular version and then
# add a `version` specification to a standard.

import codecs
import os
import yaml

from ansiblereview import Result, Error, Standard, lintcheck
from ansiblereview.utils.yamlindent import yamlreview
from ansiblereview.inventory import parse, no_vars_in_host_file
from ansiblereview.code import code_passes_flake8
from ansiblereview.vars import repeated_vars
from ansiblereview.playbook import repeated_names
from ansiblelint.utils import normalize_task, \
    parse_yaml_linenumbers, get_action_tasks


def yaml_form_rather_than_key_value(candidate, settings):
    with codecs.open(candidate.path, mode='rb', encoding='utf-8') as f:
        content = parse_yaml_linenumbers(f.read(), candidate.path)
    errors = []
    if content:
        fileinfo = dict(type=candidate.filetype, path=candidate.path)
        for task in get_action_tasks(content, fileinfo):
            normal_form = normalize_task(task, candidate.path)
            action = normal_form['action']['__ansible_module__']
            arguments = normal_form['action']['__ansible_arguments__']
            # FIXME: This is a bug - perhaps when connection is local
            # or similar
            if action not in task:
                continue
            if isinstance(task[action], dict):
                continue
            if task[action] != ' '.join(arguments):
                errors.append(Error(task['__line__'], "Task arguments appear "
                                    "to be in key value rather "
                                    "than YAML format"))
    return Result(candidate.path, errors)


def files_should_have_actual_content(candidate, settings):
    errors = []
    with codecs.open(candidate.path, mode='rb', encoding='utf-8') as f:
        content = yaml.load(f.read())
    if not content:
        errors = [Error(0, "%s appears to have no useful content" % candidate)]
    return Result(candidate.path, errors)


def metamain(candidate, settings):
    try:
        fh = codecs.open(candidate.path, mode='rb', encoding='utf-8')
    except IOError, e:
        result = Result(candidate)
        result.errors = [Error(None, "Could not open %s: %s" %
                               (candidate.path, e))]
    try:
        result = Result(candidate)
        data = yaml.safe_load(fh)
        if 'dependencies' in data:
            if data["dependencies"] == []:
                return result
            else:
                result.errors = [Error(None, "Role dependencies are "
                                             "not empty")]
        else:
            result.errors = [Error(None, "Role meta/main.yml does "
                                         "not contain a dependencies section")]
    except Exception, e:
        result.errors = [Error(None, "Could not parse in %s: %s" %
                               (candidate.path, e))]
    finally:
        fh.close()
    return result


def yamlrolesfile(candidate, settings):
    rolesfile = os.path.join(os.path.dirname(candidate.path), "rolesfile")
    result = Result(candidate)
    if os.path.exists(rolesfile) and not os.path.exists(rolesfile + ".yml"):
        result.errors = [Error(None, "Rolesfile %s does not "
                                     "have a yaml extension" % rolesfile)]
        return result
    rolesfile = os.path.join(os.path.dirname(candidate.path), "rolesfile.yml")
    if os.path.exists(rolesfile):
        with codecs.open(rolesfile, mode='rb', encoding='utf-8') as f:
            try:
                yaml.safe_load(f)
            except Exception, e:
                result.errors = [Error(None, "Cannot parse YAML from %s: %s" %
                                       (rolesfile, str(e)))]
    return result


def playbook_contains_logic(candidate, settings):
    errors = []
    with codecs.open(candidate.path, mode='rb', encoding='utf-8') as f:
        plays = parse_yaml_linenumbers(f.read(), candidate.path)
    for logic in ['tasks', 'pre_tasks', 'post_tasks', 'vars', 'handlers']:
        for play in plays:
            if logic in play:
                if isinstance(play[logic], list):
                    firstitemline = play[logic][0]['__line__'] - 1
                elif isinstance(play[logic], dict):
                    firstitemline = play[logic]['__line__']
                else:
                    continue
                # we can only access line number of first thing in the section
                # so we guess the section starts on the line above. 
                errors.append(Error(firstitemline,
                                    "%s should not be required in a play" %
                                    logic))

    return Result(candidate.path, errors)


def rolesfile_contains_scm_in_src(candidate, settings):
    result = Result(candidate.path)
    if candidate.path.endswith(".yml") and os.path.exists(candidate.path):
        try:
            with codecs.open(candidate.path, mode='rb', encoding='utf-8') as f:
                roles = parse_yaml_linenumbers(f.read(), candidate.path)
            for role in roles:
                if '+' in role.get('src'):
                    error = Error(role['__line__'], "Use scm key rather "
                                  "than src: scm+url")
                    result.errors.append(error)
        except Exception, e:
            result.errors = [Error(None, "Cannot parse YAML from %s: %s" %
                                   (candidate.path, str(e)))]
    return result


def host_vars_exist(candidate, settings):
    return Result(candidate.path, [Error(0, "Host vars are generally not required")])


rolesfile_should_be_in_yaml = Standard(dict(
    name="Roles file should be in yaml format",
    check=yamlrolesfile,
    types=["rolesfile"]
))

role_must_contain_meta_main = Standard(dict(
    name="Roles must contain suitable meta/main.yml",
    check=metamain,
    types=["meta"]
))

commands_should_be_idempotent = Standard(dict(
    name="Commands should be idempotent",
    check=lintcheck('ANSIBLE0012'),
    types=["playbook", "task"]
))

commands_should_not_be_used_in_place_of_modules = Standard(dict(
    name="Commands should not be used in place of modules",
    check=lintcheck('ANSIBLE0006,ANSIBLE0007'),
    types=["playbook", "task", "handler"]
))

package_installs_should_not_use_latest = Standard(dict(
    name="Package installs should use present, not latest",
    check=lintcheck('ANSIBLE0010'),
    types=["playbook", "task", "handler"]
))

use_shell_only_when_necessary = Standard(dict(
    name="Shell should only be used when essential",
    check=lintcheck('ANSIBLE0013'),
    types=["playbook", "task", "handler"]
))

files_should_be_indented = Standard(dict(
    name="YAML should be correctly indented",
    check=yamlreview,
    types=["playbook", "task", "handler", "rolevars",
           "hostvars", "groupvars", "meta"]
))

inventory_must_parse = Standard(dict(
    name="Inventory must be parseable",
    check=parse,
    types=["inventory"]
))

inventory_hostfiles_should_not_contain_vars = Standard(dict(
    name="Inventory host files should not "
         "contain variable stanzas ([group:vars])",
    check=no_vars_in_host_file,
    types=["inventory"]
))

code_should_meet_flake8 = Standard(dict(
    name="Python code should pass flake8",
    check=code_passes_flake8,
    types=["code"]
))

tasks_are_named = Standard(dict(
    name="Tasks and handlers must be named",
    check=lintcheck('ANSIBLE0011'),
    types=["playbook", "task", "handler"],
))

tasks_are_uniquely_named = Standard(dict(
    name="Tasks and handlers must be uniquely named within a single file",
    check=repeated_names,
    types=["playbook", "task", "handler"],
))

vars_are_not_repeated_in_same_file = Standard(dict(
    name="Vars should only occur once per file",
    check=repeated_vars,
    types=["rolevars", "hostvars", "groupvars"],
))

no_command_line_environment_variables = Standard(dict(
    name="Environment variables should be passed through the environment key",
    check=lintcheck('ANSIBLE0014'),
    types=["playbook", "task", "handler"]
))

become_rather_than_sudo = Standard(dict(
    name="Use become/become_user/become_method rather than sudo/sudo_user",
    check=lintcheck('ANSIBLE0008'),
    types=["playbook", "task", "handler"]
))

use_yaml_rather_than_key_value = Standard(dict(
    name="Use YAML format for tasks and handlers rather than key=value",
    check=yaml_form_rather_than_key_value,
    types=["playbook", "task", "handler"]
))

roles_scm_not_in_src = Standard(dict(
    name="Use scm key rather than src: scm+url",
    check=rolesfile_contains_scm_in_src,
    types=["rolesfile"]
))

files_should_not_be_purposeless = Standard(dict(
    name="Files should contain useful content",
    check=files_should_have_actual_content,
    types=["playbook", "task", "handler", "rolevars", "defaults", "meta"]
))

playbooks_should_not_contain_logic = Standard(dict(
    name="Playbooks should not contain logic (vars, tasks, handlers)",
    check=playbook_contains_logic,
    types=["playbook"]
))

host_vars_should_not_be_present = Standard(dict(
    name="Host vars should not be present",
    check=host_vars_exist,
    types=["hostvars"]
))

ansible_review_min_version = '0.7.0'

standards = [
    rolesfile_should_be_in_yaml,
    role_must_contain_meta_main,
    become_rather_than_sudo,
    commands_should_be_idempotent,
    commands_should_not_be_used_in_place_of_modules,
    package_installs_should_not_use_latest,
    files_should_be_indented,
    use_shell_only_when_necessary,
    inventory_must_parse,
    inventory_hostfiles_should_not_contain_vars,
    code_should_meet_flake8,
    tasks_are_named,
    tasks_are_uniquely_named,
    vars_are_not_repeated_in_same_file,
    no_command_line_environment_variables,
    use_yaml_rather_than_key_value,
    roles_scm_not_in_src,
    files_should_not_be_purposeless,
    playbooks_should_not_contain_logic,
    host_vars_should_not_be_present,
]

