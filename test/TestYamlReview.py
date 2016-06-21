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

    def test_yaml_success(self):
        candidate = Playbook(os.path.join(self.directory, 'yaml_success.yml'))
        settings = Settings({})
        result = yamlreview(candidate, settings)
        self.assertEqual(len(result.errors), 0)
