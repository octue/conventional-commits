import unittest
from unittest.mock import mock_open, patch

from pre_commit_hooks.conventional_commits.cli import main


class TestCLI(unittest.TestCase):
    def test_main_with_valid_commit_message(self):
        """Test that the entrypoint works with a valid commit message."""
        with patch("pre_commit_hooks.conventional_commits.cli.open", mock_open(read_data="FIX: Fix a bug")):
            return_code = main()

        self.assertEqual(return_code, 0)

    def test_main_with_invalid_commit_message(self):
        """Test that an error is raised by the entrypoint when an invalid commit message is given."""
        with patch("pre_commit_hooks.conventional_commits.cli.open", mock_open(read_data="blah\nawful commit message")):
            return_code = main()

        self.assertEqual(return_code, 1)
