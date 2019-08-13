#!/usr/bin/env python

"""
Quick and dirty YAML checker.
Verifies that lines only increase indentation by 2
and that lines starting '- ' don't have additional
indentation.
Blank lines are ignored.

GOOD:

```
- tasks:
  - name: hello world
    command: echo hello

  - name: another task
    debug:
      msg: hello
```

BAD:

```
- tasks:
   # comment in random indentation
    - name: hello world
      debug:
          msg: hello
```
"""


from __future__ import print_function
import codecs
import re
import sys
from ansiblereview import Result, Error, utils


def indent_checker(filename, indent_list_items):
    with codecs.open(filename, mode='rb', encoding='utf-8') as f:
        indent_regex = re.compile(r"^(?P<indent>\s*(?:- )?)(?P<rest>.*)$")
        lineno = 0
        prev_indent = ''
        errors = []
        for line in f:
            lineno += 1
            match = indent_regex.match(line)
            if len(match.group('rest')) == 0:
                continue
            curr_indent = match.group('indent')
            offset = len(curr_indent) - len(prev_indent)
            if offset > 0:
                if match.group('indent').endswith('- '):
                    if indent_list_items and offset != 4 and match.group('indent') != '- ':
                        errors.append(Error(lineno, "indentation should increase by 2 chars "
                                            "(indent_list_items is True)"))
                    if not indent_list_items and offset != 2:
                        errors.append(Error(lineno, "lines starting with '- ' should have same "
                                                    "or less indentation than previous line "
                                                    "(indent_list_items is False)"))
                elif offset != 2:
                    errors.append(Error(lineno, "indentation should increase by 2 chars"))
            prev_indent = curr_indent
        return errors


def yamlreview(candidate, settings):
    errors = indent_checker(candidate.path, settings.indent_list_items)
    return Result(candidate.path, errors)


if __name__ == '__main__':
    args = sys.argv[1:] or [sys.stdin]
    rc = 0
    for arg in args:
        result = yamlreview(arg, utils.Settings())
        for error in result.errors():
            print("ERROR: %s:%s: %s" % (arg, error.lineno, error.message), file=sys.stderr)
            rc = 1
    sys.exit(rc)
