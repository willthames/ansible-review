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

from ansiblereview import Error, Result, utils


def indent_checker(filename):
    with codecs.open(filename, mode='rb', encoding='utf-8') as f:
        indent_regex = re.compile("^(?P<indent>\s*(?:- )?)(?P<rest>.*)$")
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
            if offset > 0 and offset != 2:
                if match.group('indent').endswith('- '):
                    errors.append(Error(lineno, "lines starting with '- ' should have same "
                                        "or less indentation than previous line",
                                  error_type='yamlreview'))
                else:
                    errors.append(Error(lineno, "indentation should increase by 2 chars",
                                  error_type='yamlreview'))
            prev_indent = curr_indent
        return errors


def yamlreview(candidate, settings):
    errors = indent_checker(candidate.path)
    return Result(candidate.path, errors)


if __name__ == '__main__':
    args = sys.argv[1:] or [sys.stdin]
    rc = 0
    for arg in args:
        result = yamlreview(arg, utils.Settings(utils.read_config()))
        for error in result.errors():
            print("ERROR: %s:%s: %s" % (arg, error.lineno, error.message), file=sys.stderr)
            rc = 1
    sys.exit(rc)
