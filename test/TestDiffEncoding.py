import unittest
import os
import io
import ansiblereview.__main__ as main

class TestDiffEncoding(unittest.TestCase):

    directory = os.path.dirname(__file__)
    
    def test_diff_encoding(self):
        difflines = []
        with io.open(os.path.join(self.directory, 'diff.txt'), 'r') as f:
            for line in f.readlines():
                encodedline = line.encode("utf-8")
                difflines.append(encodedline)
            candidate = main.get_candidates_from_diff(difflines)
            self.assertEqual(len(candidate), 1)
