import os
from tests import TESTS_ROOT
import unittest
from conventional_commits.cli import main


class TestCLI(unittest.TestCase):

    def test_main_with_valid_commit_message(self):
        return_code = main([os.path.join(TESTS_ROOT, "fixtures", "valid_commit_message")])
        self.assertEqual(return_code, 0)

    def test_main_with_invalid_commit_message(self):
        return_code = main([os.path.join(TESTS_ROOT, "fixtures", "invalid_commit_message")])
        self.assertEqual(return_code, 1)
