import unittest
import os
import sys
import io
import mock
import ansiblereview.__main__ as main


def patch_stdin_with(file_name):
    def decorator(func):
        def stdin_patcher(*args, **kwargs):
            with io.open(file_name, 'rb') as f:
                mock_stream = (
                    io.TextIOWrapper if sys.version_info[0] == 3
                    else io.BufferedReader
                )(f)

                with mock.patch.object(sys, 'stdin', mock_stream):
                    return func(*args, **kwargs)
        return stdin_patcher
    return decorator


class TestDiffEncoding(unittest.TestCase):

    directory = os.path.dirname(__file__)
    
    def test_diff_encoding(self):
        difflines = []
        with io.open(os.path.join(self.directory, 'diff.txt'), 'r', encoding='utf-8') as f:
            for line in f.readlines():
                encodedline = line.encode("utf-8")
                difflines.append(encodedline)
            candidate = main.get_candidates_from_diff(difflines)
            self.assertEqual(len(candidate), 1)

    @mock.patch.object(sys, 'argv', [sys.argv[0]])  # Enter stdin read mode
    @patch_stdin_with(os.path.join(directory, 'diff.txt'))
    def test_diff_stdin_encoding(self):
        errors_num = main.main()
        assert errors_num == 0
