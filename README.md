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
ansible-review reviewtarget [target2...]
```

ansible-review will review inventory files, role
files, python code (modules, plugins) and playbooks.

* The goal is that each file that changes in a
  changeset should be reviewable simply by passing
  those files as the arguments to ansible-review.
* Roles are slightly harder, and sub-roles are yet
  harder still (currently just using `-R` to process
  roles works very well, but doesn't examine the
  structure of the role)
* Using `{{ playbook_dir }}` in sub roles is so far
  very hard.
* This should work against various repository styles
  - per-role repository
  - roles with sub-roles
  - per-playbook repository
* It should work with rolesfiles and with local roles.

## Typical approaches

* `git ls-files | xargs ansible-review` works well in
  a roles repo to review the whole role. But it will
  review the whole of other repos too.
* `git diff branch_to_compare | ansible-review` will
  review only the changes between the branches and
  surrounding context.


# Reviews

Reviews are nothing without some standards or checklists
against which to review.

ansible-review comes with a couple of built-in checks, such as
a playbook syntax checker and a hook to ansible-lint. You define your
own standards.

## Configuration

If your standards (and optionally inhouse lint rules) are set up, create
a configuration file in the appropriate location (this will depend on
your operating system)

The location can be found by using `ansible-review` with no arguments.

You can override the configuration file location with the `-c` flag.

```
[rules]
lint = /path/to/your/ansible/lint/rules
standards = /path/to/your/standards/rules
```


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
    types = ['playbook', 'task'],
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

An example standards file is available in
[examples/standards.py](examples/standards.py)

## Standards checks

A typical standards check will look like:

```
def check_playbook_for_something(candidate, settings):
    result = Result(candidate.path) # empty result is a success with no output
    with open(candidate.path, 'r') as f:
        for (lineno, line) in enumerate(f):
            if line is dodgy:
                # enumerate is 0-based so add 1 to lineno
                result.errors.append(Error(lineno+1, "Line is dodgy: reasons"))
    return result
```

All standards check take a candidate object, which has a path attribute.
The type can be inferred from the class name (i.e. `type(candidate).__name__`)

The ansiblelint check is ready out of the box, and just takes a list of
IDs or tags to check. You can point to your own ansible-lint rules
using the configuration file or `-d /path/to/ansible/lint/rules`
