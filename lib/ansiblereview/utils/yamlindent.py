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
import re
import sys
from ansiblereview import Result


def error_msg(message, lineno, filename, show_file):
    if show_file:
        output = "{0}: line {1}: {2}".format(filename, lineno, message)
    else:
        output = "line {0}: {1}".format(lineno, message)
    return output


def indent_checker(filename, show_file=False):
    with open(filename, 'r') as f:
        indent_regex = re.compile("^(?P<whitespace>\s*)(?P<rest>.*)$")
        lineno = 0
        prev_indent = 0
        errors = []
        for line in f:
            lineno += 1
            match = indent_regex.match(line)
            if len(match.group('rest')) == 0:
                continue
            match = indent_regex.match(line)
            curr_indent = len(match.group('whitespace'))
            if curr_indent - prev_indent > 0:
                if match.group('rest').startswith('- '):
                    errors.append(
                        error_msg("lines starting with '- ' should have same "
                                  "or less indentation than previous line",
                                  lineno, filename, show_file))
                elif curr_indent - prev_indent != 2:
                    errors.append(
                        error_msg("indentation should only increase by 2 chars",
                                  lineno, filename, show_file))
            prev_indent = curr_indent
        return errors


def yamlreview(filename, settings):
    errors = indent_checker(filename)
    result = Result()
    if errors:
        result.failed = True
        result.stderr = "\n".join(errors)
        result.stdout = ""
    return result


if __name__ == '__main__':
    args = sys.argv[1:] or [sys.stdin]
    rc = 0
    for arg in args:
        for error in indent_checker(arg, len(args) > 1):
            print("ERROR: " + error, file=sys.stderr)
            rc = 1
    sys.exit(rc)
