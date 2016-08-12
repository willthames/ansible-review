from ansiblereview import Standard, Result, Error, lintcheck
from ansiblereview.groupvars import same_variable_defined_in_competing_groups


def check_fail(candidate, settings):
    return Result(candidate,[Error(1, "test failed")])


def check_success(candidate, settings):
    return Result(candidate)

test_task_ansiblelint_success = Standard(dict(
    check = lintcheck('TEST0002'),
    name = "Test task lint success",
    version = "0.2",
    types = ["playbook", "tasks", "handlers"]
))

test_task_ansiblelint_failure = Standard(dict(
    check = lintcheck('TEST0001'),
    name = "Test task lint failure",
    version = "0.4",
    types = ["playbook", "tasks", "handlers"]
))

test_failure = Standard(dict(
    check = check_fail,
    name = "Test general failure",
    version = "0.5",
    types=["playbook", "task", "handler", "rolevars",
           "hostvars", "groupvars", "meta"]
))

test_success = Standard(dict(
    check = check_success,
    name = "Test general success",
    version = "0.2",
    types = "playbook,tasks,vars"
))

test_matching_groupvar = Standard(dict(
    check = same_variable_defined_in_competing_groups,
    name = "Same variable defined in siblings",
    types = "groupvars"
))



standards = [
        test_task_ansiblelint_success,
        test_task_ansiblelint_failure,
        test_success,
        test_failure,
        test_matching_groupvar,
]
