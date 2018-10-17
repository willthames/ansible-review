# Setup

## Using pip

```
pip install ansible-review
```

## From source

```
# Install dependency https://github.com/willthames/ansible-lint
git clone https://github.com/willthames/ansible-review
export PYTHONPATH=$PYTHONPATH:`pwd`/ansible-review/lib
export PATH=$PATH:`pwd`/ansible-review/bin
```

## Fedora/RHEL

ansible-review can be found: under standard Fedora repos, or under [EPEL](http://fedoraproject.org/wiki/EPEL#How_can_I_use_these_extra_packages.3F).
To install ansible-review, use yum or dnf accordingly.

```
yum install ansible-review
```

# Usage

```
ansible-review FILES
```

Where FILES is a space delimited list of files to review.
ansible-review is _not_ recursive and won't descend
into child folders; it just processes the list of files you give it.

Passing a folder in with the list of files will elicit a warning:

```
WARN: Couldn't classify file ./foldername
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
* It should work with roles requirement files and with local roles

## Typical approaches

### Git repositories

* `git ls-files | xargs ansible-review` works well in
  a roles repo to review the whole role. But it will
  review the whole of other repos too.
* `git diff branch_to_compare | ansible-review` will
  review only the changes between the branches and
  surrounding context.

### Without git

* `find . -type f | xargs ansible-review` will review
  all files in the current folder (and all subfolders),
  even if they're not checked into git

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

The standards directory can be overridden with the `-d` argument,
and the lint rules directory can be overwritten with the `-r` argument.


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
using, otherwise ansible-review assumes you're using the latest. The declaration
is done by adding standards version as first line in the file. e.g.

```
# Standards: 1.2
```

To add standards that are advisory, don't set the version. These will cause
a message to be displayed but won't constitute a failure.

When a standard version is higher than declared version, a message will be
displayed 'WARN: Future standard' and won't constitute a failure.

An example standards file is available at
[lib/ansiblereview/examples/standards.py](lib/ansiblereview/examples/standards.py)

If you only want to check one or two standards quickly (perhaps you want
to review your entire code base for deprecated bare words), you can use the
`-s` flag with the name of your standard. You can pass `-s` multiple times.

```
git ls-files | xargs ansible-review -s "bare words are deprecated for with_items"
```

You can see the name of the standards being checked for each different file by running
`ansible-review` with the `-v` option.


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

They return a `Result` object, which contains a possibly empty list of `Error`
objects. `Error` objects are formed of a line number and a message. If the
error applies to the whole file being reviewed, set the line number to `None`.
Line numbers are important as `ansible-review` can review just ranges of files
to only review changes (e.g. through piping the output of `git diff` to
`ansible-review`)

The ansible-lint check is ready out of the box, and just takes a list of
IDs or tags to check. You can point to your own ansible-lint rules
using the configuration file or `-d /path/to/ansible/lint/rules`

# Pre-commit

To use ansible-review with [pre-commit](https://pre-commit.com/), just
add the following to your local repo's `.pre-commit-config.yaml` file.
Make sure to change `sha:` to be either a git commit SHA or tag of
ansible-review containing `hooks.yaml`.

```yaml
- repo: https://github.com/willthames/ansible-review
  sha: bd2e8b6863dc20d8619418e6817d5793c7ebc687
  hooks:
    - id: ansible-review
```

Notice, that this is currently in testing phase.
