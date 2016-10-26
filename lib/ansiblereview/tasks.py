import codecs
from ansiblereview import Result, Error
from ansiblelint.utils import get_action_tasks, normalize_task, \
    parse_yaml_linenumbers


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
            # Cope with `set_fact` where task['set_fact'] is None
            if not task.get(action):
                continue
            if isinstance(task[action], dict):
                continue
            # strip additional newlines off task[action]
            if task[action].strip().split() != arguments:
                errors.append(Error(task['__line__'], "Task arguments appear "
                                    "to be in key value rather "
                                    "than YAML format"))
    return Result(candidate.path, errors)
