from ansiblereview import Standard, Result, Error, lintcheck


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


standards = [
        test_task_ansiblelint_success,
        test_task_ansiblelint_failure,
        test_success,
        test_failure,
]
