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
import subprocess

from testfixtures import log_capture

try:
    from ansible.utils.color import stringc
except ImportError:
    from ansible.color import stringc

from ansiblereview import classify, Task
from ansiblereview.utils import load_display_handler
import ansiblereview.code as code


class Options(object):
    pass


class TestJsonOutput(unittest.TestCase):

    def setUp(self):
        self.cwd = os.path.dirname(__file__)
        self.options = Options()
        self.options.lintdir = os.path.join(self.cwd, '..', 'lib',
            'ansiblereview', 'examples', 'lint-rules')
        self.options.rulesdir = os.path.join(self.cwd, 'example_standards')
        self.options.standards_filter = []
        self.display = load_display_handler('json', 'testing', logging.DEBUG)

    @log_capture()
    def test_tag_exists_in_output(self, capture):
        candidate_path = os.path.join(self.cwd, 'test_cases', 'test_role_errors',
                                      'tasks', 'main.yml')
        candidate = classify(candidate_path)
        candidate.review(self.options, None, display=self.display)
        for actual in capture.actual():
            data = json.loads(actual[2])
            self.assertIsInstance(data, dict)
            self.assertIn('tag', data)

    @log_capture()
    def test_ansiblelint_present(self, capture):
        candidate_path = os.path.join(self.cwd, 'test_cases', 'test_role_errors',
                                      'tasks', 'main.yml')
        candidate = classify(candidate_path)
        candidate.review(self.options, None, display=self.display)
        count = 0
        for actual in capture.actual():
            data = json.loads(actual[2])
            if ('error_type' in data and data['error_type'] == 'ansiblelint'):
                count += 1
                self.assertIn('lineno', data)
                self.assertIn('error_msg', data)
                self.assertIn('error_rule', data)
        self.assertEqual(count, 3)
    
    @log_capture()
    def test_yamlreview_present(self, capture):
        candidate_path = os.path.join(self.cwd, 'test_cases', 'test_role_errors',
                                      'defaults', 'main.yml')
        candidate = classify(candidate_path)
        candidate.review(self.options, None, display=self.display)
        count = 0
        for actual in capture.actual():
            data = json.loads(actual[2])
            if ('error_type' in data and data['error_type'] == 'yamlreview'):
                count += 1
                self.assertIn('lineno', data)
                self.assertIn('message', data)
        self.assertEqual(count, 2)
