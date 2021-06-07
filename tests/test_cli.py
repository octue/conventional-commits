import unittest
from unittest.mock import mock_open, patch

from pre_commit_hooks.conventional_commits.cli import main


class TestCLI(unittest.TestCase):
    def test_main_with_invalid_commit_message(self):
        """Test that an error is raised by the entrypoint when an invalid commit message is given."""
        with patch("pre_commit_hooks.conventional_commits.cli.open", mock_open(read_data="blah\nawful commit message")):
            return_code = main()

        self.assertEqual(return_code, 1)

    def test_main_with_valid_commit_message(self):
        """Test that the entrypoint works with a valid commit message."""
        with patch("pre_commit_hooks.conventional_commits.cli.open", mock_open(read_data="FIX: Fix a bug")):
            return_code = main()

        self.assertEqual(return_code, 0)

    def test_with_maximum_header_length_violated(self):
        """Test an error is raised when the specified maximum header length is violated."""
        with patch("pre_commit_hooks.conventional_commits.cli.open", mock_open(read_data="FIX: Fix a bug")):
            return_code = main(["--maximum-header-length=1"])

        self.assertEqual(return_code, 1)

    def test_with_valid_header_ending_pattern_violated(self):
        """Test an error is raised when the specified header-ending-pattern is violated."""
        with patch("pre_commit_hooks.conventional_commits.cli.open", mock_open(read_data="FIX: Fix a bug")):
            return_code = main(["--valid-header-ending-pattern=@"])

        self.assertEqual(return_code, 1)

    def test_with_require_body_violated(self):
        """Test an error is raised when a body is not provided when it is required."""
        with patch("pre_commit_hooks.conventional_commits.cli.open", mock_open(read_data="FIX: Fix a bug")):
            return_code = main(["--require-body=1"])

        self.assertEqual(return_code, 1)

    def test_with_maximum_body_line_length_violated(self):
        """Test an error is raised when the specified maximum body line length is violated."""
        with patch("pre_commit_hooks.conventional_commits.cli.open", mock_open(read_data="FIX: Fix a bug\n\nhello")):
            return_code = main(["--maximum-body-line-length=1"])

        self.assertEqual(return_code, 1)
