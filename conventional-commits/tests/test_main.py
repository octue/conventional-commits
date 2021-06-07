import os
from tests import TESTS_ROOT
import unittest
from conventional_commits.cli import main


class TestCLI(unittest.TestCase):

    def test_main_with_valid_commit_message(self):
        error_code = main([os.path.join(TESTS_ROOT, "valid_commit_message")])
        self.assertEqual(error_code, 0)

    def test_main_with_invalid_commit_message(self):
        error_code = main([os.path.join(TESTS_ROOT, "invalid_commit_message")])
        self.assertEqual(error_code, 1)
