import unittest
from unittest.mock import mock_open, patch

from pre_commit_hooks.conventional_commits.cli import main


class TestCLI(unittest.TestCase):
    def test_with_invalid_commit_message(self):
        """Test that an error is raised by the entrypoint when an invalid commit message is given."""
        with patch("pre_commit_hooks.conventional_commits.cli.open", mock_open(read_data="blah\nawful commit message")):
            return_code = main()

        self.assertEqual(return_code, 1)

    def test_with_valid_commit_message(self):
        """Test that the entrypoint works with a valid commit message."""
        with patch("pre_commit_hooks.conventional_commits.cli.open", mock_open(read_data="FIX: Fix a bug")):
            return_code = main()

        self.assertEqual(return_code, 0)

    def test_with_different_allowed_commit_codes(self):
        """Test that custom commit codes can be provided to replace the default set."""
        custom_commit_codes = "ABC", "DEF", "GHI"

        # Ensure the custom commit codes work.
        for code in custom_commit_codes:
            with patch("pre_commit_hooks.conventional_commits.cli.open", mock_open(read_data=f"{code}: Do a thing")):
                return_code = main([f"--allowed-commit-codes={','.join(custom_commit_codes)}"])
                self.assertEqual(return_code, 0)

        # Ensure a default code now fails.
        with patch("pre_commit_hooks.conventional_commits.cli.open", mock_open(read_data="DOC: Update docs")):
            return_code = main([f"--allowed-commit-code={','.join(custom_commit_codes)}"])
            self.assertEqual(return_code, 1)

    def test_with_additional_allowed_commit_codes(self):
        """Test that additional commit codes can be provided to augment the default set."""
        additional_code = "ABC"

        # Ensure the additional code works.
        with patch("pre_commit_hooks.conventional_commits.cli.open", mock_open(read_data="ABC: Do a thing")):
            return_code = main([f"--additional-commit-codes={additional_code}"])
            self.assertEqual(return_code, 0)

        # Ensure a default code still works.
        with patch("pre_commit_hooks.conventional_commits.cli.open", mock_open(read_data="DOC: Update docs")):
            return_code = main([f"--additional-commit-codes={additional_code}"])
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
