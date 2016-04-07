# Setup

## Using pip

```
pip install ansible-review
```

## From source

```
git clone https://github.com/willthames/ansible-review
export $PYTHONPATH=$PYTHONPATH:`pwd`/lib
export $PATH=$PATH:`pwd`/bin
```


# Usage

```
ansible-review reviewtarget
```

ansible-review will review inventory directories, role
directories and playbooks.

# Reviews

Reviews are nothing without some standards or checklists
against which to review.

ansible-review comes with a couple of built-in checks, such as
a playbook syntax checker and a hook to ansible-lint. You define your
own standards.

## Standards file

A standards file comprises a list of standards, and optionally some methods to
check those standards.

Create a file called standards.py (this can import other modules)

```
from ansiblereview include Standard, Result

use_modules_instead_of_command = Standard(dict(
    name = "Use modules instead of commands",
    version = "0.2",
    check = ansiblelint('ANSIBLE0005,ANSIBLE0006'),
    types = ['playbook', 'role'],
))

standards = [
  use_modules_instead_of_command,
  packages_should_not_be_latest,
]
```

When you add new standards, you should increment the version of your standards.
Your playbooks and roles should declare what version of standards you are
using, otherwise ansible-review assumes you're using the latest.

To add standards that are advisory, don't set the version. These will cause
a message to be displayed but won't constitute a failure.

## Standards checks

A typical standards check will look like:

```
def check_playbook_for_something(playbookfile, settings):
    result = Result() # empty result is a success with no output
    with open(playbookfile, 'r') as f:
        do_something
        if unexpected:
            result.failed = True
            result.stderr = "Something unexpected happened in %s" % playbook
    return result

def check_role_for_something(rolesdir, settings):
    result = Result()
    look_for_file_in_role_doing_something
    if unexpected:
        result.failed = True
        result.stderr = "Weird stuff in role %s" % rolesdir
    return result
```

The ansiblelint check is ready out of the box, and just takes a list of
IDs or tags to check. You can add your own ansible-lint rules in a directory
and then pass `-d /path/to/ansible/lint/rules` 

# TODO

* Add configuration file for ansible lint rules path and ansible review rules
path.



