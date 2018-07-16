# Copyright (c) 2013-2014 Will Thames <will@thames.id.au>
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.

import json
import logging
import os
import unittest

from testfixtures import log_capture

try:
    from ansible.utils.color import stringc
except ImportError:
    from ansible.color import stringc

from ansiblereview import Playbook, Task, Code
from ansiblereview.utils import load_display_handler
import ansiblereview.code as code


class TestUtils(unittest.TestCase):
    def setUp(self):
        self.cwd = os.path.dirname(__file__)

    def test_find_version_playbook(self):
        candidate = Playbook(os.path.join(self.cwd, 'test_cases', 'test_playbook_0.2.yml'))
        self.assertEqual(candidate.version, '0.2')

    def test_find_version_rolefile(self):
        candidate = Task(os.path.join(self.cwd, 'test_cases', 'test_role_v0.2',
                                      'tasks', 'main.yml'))
        self.assertEqual(candidate.version, '0.2')

    def test_code_passes_flake8(self):
        # run flake8 against this source file
        candidate = Code(__file__.replace('.pyc', '.py'))
        result = code.code_passes_flake8(candidate, None)
        self.assertEqual(len(result.errors), 0)

    @log_capture()
    def test_default_display(self, capture):
        display = load_display_handler('default', 'hello', logging.DEBUG)
        display.info("Hello World!")
        display.warn("Hello Again")
        display.error("Yikes!")
        capture.check(
            ('hello', 'INFO', stringc('INFO: Hello World!', 'green')),
            ('hello', 'WARNING', stringc('WARN: Hello Again', 'yellow')),
            ('hello', 'ERROR', stringc('ERROR: Yikes!', 'red'))
        )

    @log_capture()
    def test_json_display(self, capture):
        display = load_display_handler('json', 'json_logger', logging.DEBUG)
        display.info("Hello World!", tag="hi")
        data = json.loads(capture.actual()[-1][-1])
        self.assertEqual(data['tag'], 'hi')
        self.assertEqual(data['event'], 'Hello World!')
