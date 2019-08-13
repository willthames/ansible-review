import unittest
import os
from ansiblereview.utils.yamlindent import yamlreview
from ansiblereview.utils import Settings
from ansiblereview import Playbook

class TestYamlReview(unittest.TestCase):

    directory = os.path.dirname(__file__)

    def test_yaml_failures(self):
        candidate = Playbook(os.path.join(self.directory, 'yaml_fail.yml'))
        settings = Settings({})
        result = yamlreview(candidate, settings)
        self.assertEqual(len(result.errors), 3)

    def test_yaml_no_indent_list(self):
        candidate = Playbook(os.path.join(self.directory, 'yaml_no_indent_list.yml'))
        settings = Settings({})
        result = yamlreview(candidate, settings)
        self.assertEqual(len(result.errors), 0)

    def test_yaml_indent_list(self):
        candidate = Playbook(os.path.join(self.directory, 'yaml_indent_list.yml'))
        settings = Settings({})
        settings.indent_list_items = True
        result = yamlreview(candidate, settings)
        self.assertEqual(len(result.errors), 0)
