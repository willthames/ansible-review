import unittest
import os
from ansiblereview.utils import Settings
from ansiblereview import Inventory
from ansiblereview.inventory import parse


class TestInventory(unittest.TestCase):

    def setUp(self):
        self.cwd = os.path.dirname(__file__)

    def test_inventory_parses(self):
        candidate = Inventory(os.path.join(self.cwd, 'test_cases', 'hosts'))
        settings = Settings({})
        result = parse(candidate, settings)
        self.assertEqual(len(result.errors), 0)
