import unittest
from unittest.mock import mock_open, patch

from conventional_commits.check_commit_message import ConventionalCommitMessageChecker, main


class TestCheckCommitMessage(unittest.TestCase):
    def test_empty_commit_message_raises_error(self):
        """Test that an empty commit message results in an error."""
        with self.assertRaises(ValueError):
            ConventionalCommitMessageChecker().check_commit_message([])

    def test_header_but_no_body_when_body_is_required_raises_error(self):
        """Test that a commit message with a header but no body when the body is required results in an error."""
        with self.assertRaises(ValueError):
            ConventionalCommitMessageChecker(require_body=True).check_commit_message(["FIX: Fix this bug"])

    def test_with_header_but_no_body_when_body_is_not_required(self):
        """Test that a commit message with a header but no body when the body is not required results is ok."""
        ConventionalCommitMessageChecker().check_commit_message(["FIX: Fix this bug"])

    def test_empty_header_raises_error(self):
        """Test that a commit message with an empty header results in an error."""
        with self.assertRaises(ValueError):
            ConventionalCommitMessageChecker().check_commit_message([""])

    def test_invalid_commit_code_raises_error(self):
        """Test that a commit message with an invalid commit code results in an error."""
        with self.assertRaises(ValueError):
            ConventionalCommitMessageChecker().check_commit_message(["BLAH: This is a blah commit"])

    def test_header_over_maximum_length_raises_error(self):
        """Test that a commit message with a header that is too long results in an error."""
        with self.assertRaises(ValueError):
            ConventionalCommitMessageChecker().check_commit_message([f"IMP: {'a' * 80}"])

    def test_invalid_header_ending_raises_error(self):
        """Test that a commit message with a header with an invalid ending results in an error."""
        with self.assertRaises(ValueError):
            ConventionalCommitMessageChecker().check_commit_message(["FIX: Fix this bug."])

    def test_valid_header_endings(self):
        """Test that a commit message with a valid header ending is ok."""
        for ending in ("'", " ", '"' "blah", "32", ")", "`"):
            with self.subTest(ending=ending):
                ConventionalCommitMessageChecker().check_commit_message(["REV: Reverts FIX: Fix a bug" + ending])

    def test_non_blank_header_separator_line_raises_error(self):
        """Test that a commit message with a non-blank header separator line results in an error."""
        with self.assertRaises(ValueError):
            ConventionalCommitMessageChecker().check_commit_message(["FIX: Fix this bug", "Body started too early."])

    def test_with_body_when_body_not_required(self):
        """Test that a commit message with a valid header and body when a body is not required is ok."""
        ConventionalCommitMessageChecker().check_commit_message(["FIX: Fix this bug", "", "This is the body."])

    def test_with_body_when_body_required(self):
        """Test that a commit message with a valid header and body when a body is required is ok."""
        ConventionalCommitMessageChecker(require_body=True).check_commit_message(
            ["FIX: Fix this bug", "", "This is the body."]
        )

    def test_empty_body_raises_error(self):
        """Test that a commit message with an empty body results in an error."""
        with self.assertRaises(ValueError):
            ConventionalCommitMessageChecker(require_body=True).check_commit_message(["FIX: Fix this bug", "", ""])

    def test_body_lines_over_maximum_length_raises_error(self):
        """Test that a commit message with a body that has a line that is too long results in an error."""
        commit_message_checker = ConventionalCommitMessageChecker(require_body=True, maximum_body_line_length=72)

        for commits in (
            ["FIX: Fix this bug", "", f"{'a' * 80}"],
            ["FIX: Fix this bug", "", "an okay line", f"{'a' * 80}"],
        ):
            with self.subTest(commits=commits):
                with self.assertRaises(ValueError):
                    commit_message_checker.check_commit_message(commits)

    def test_comments_lines_are_ignored(self):
        """Test that comment lines in the commit message are ignored."""
        ConventionalCommitMessageChecker().check_commit_message(
            [
                "FIX: Fix this bug",
                "# Please enter the commit message for your changes. Lines starting",
                "# with '#' will be ignored, and an empty message aborts the commit.",
                "#",
                "# On branch feature/add-conventional-commit-pre-commit-package",
                "# Your branch is ahead of 'origin/feature/add-conventional-commit-pre-commit-package' by 2 commits.",
                "#   (use 'git push' to publish your local commits)",
                "#",
                "# Changes to be committed:",
                "#       modified:   conventional-commits/check_commit_message.py",
                "#       modified:   tests/test_check_commit_message.py",
                "#",
            ]
        )

    def test_trailing_newline_is_ignored(self):
        """Test that a trailing newline in the commit message is ignored."""
        ConventionalCommitMessageChecker().check_commit_message(["FIX: Fix this bug", ""])

    def test_lower_case_breaking_change_indicators_raise_error(self):
        """Test that lowercase breaking change indicators result in an error."""
        with self.assertRaises(ValueError):
            ConventionalCommitMessageChecker().check_commit_message(["FIX: Fix this bug", "", "breaking change: blah"])

        with self.assertRaises(ValueError):
            ConventionalCommitMessageChecker().check_commit_message(["FIX: Fix this bug", "", "breaking-change: blah"])

    def test_breaking_change_indicators_without_full_code_separator_raise_error(self):
        """Test that valid breaking change indicators without the full code separator raise an error."""
        for breaking_change_message in (
            "BREAKING CHANGE:blah",
            "BREAKING-CHANGE:blah",
            "BREAKING CHANGE blah",
            "BREAKING-CHANGE blah",
        ):
            with self.assertRaises(ValueError):
                ConventionalCommitMessageChecker().check_commit_message(
                    ["FIX: Fix this bug", "", breaking_change_message]
                )

    def test_breaking_change_indicator_with_no_message_raises_error(self):
        """Test that valid breaking change indicators without the full code separator raise an error."""
        for breaking_change_message in (
            "BREAKING CHANGE: ",
            "BREAKING-CHANGE: ",
        ):
            with self.assertRaises(ValueError):
                ConventionalCommitMessageChecker().check_commit_message(
                    ["FIX: Fix this bug", "", breaking_change_message]
                )

    def test_breaking_change_indicators(self):
        """Test that valid breaking change indicators with the full code separator are ok."""
        ConventionalCommitMessageChecker().check_commit_message(["FIX: Fix this bug", "", "BREAKING CHANGE: blah"])
        ConventionalCommitMessageChecker().check_commit_message(["FIX: Fix this bug", "", "BREAKING-CHANGE: blah"])

    def test_breaking_change_section_can_contain_the_words_breaking_change_after_breaking_change_indicators(self):
        """Test that the breaking change section can contain the words 'breaking change' after the breaking change
        indicator.
        """
        ConventionalCommitMessageChecker()._validate_breaking_change_descriptions(
            "BREAKING-CHANGE: Uncategorised commits contain breaking changes including the use of..."
        )


class TestMain(unittest.TestCase):
    def test_with_invalid_commit_message(self):
        """Test that an error is raised by the entrypoint when an invalid commit message is given."""
        with patch("builtins.open", mock_open(read_data="blah\nawful commit message")):
            return_code = main()

        self.assertEqual(return_code, 1)

    def test_with_valid_commit_message(self):
        """Test that the entrypoint works with a valid commit message."""
        with patch("builtins.open", mock_open(read_data="FIX: Fix a bug")):
            return_code = main()

        self.assertEqual(return_code, 0)

    def test_with_different_allowed_commit_codes(self):
        """Test that custom commit codes can be provided to replace the default set."""
        custom_commit_codes = "ABC", "DEF", "GHI"

        # Ensure the custom commit codes work.
        for code in custom_commit_codes:
            with patch("builtins.open", mock_open(read_data=f"{code}: Do a thing")):
                return_code = main([f"--allowed-commit-codes={','.join(custom_commit_codes)}"])
                self.assertEqual(return_code, 0)

        # Ensure a default code now fails.
        with patch("builtins.open", mock_open(read_data="DOC: Update docs")):
            return_code = main([f"--allowed-commit-code={','.join(custom_commit_codes)}"])
            self.assertEqual(return_code, 1)

    def test_with_additional_allowed_commit_codes(self):
        """Test that additional commit codes can be provided to augment the default set."""
        additional_code = "ABC"

        # Ensure the additional code works.
        with patch("builtins.open", mock_open(read_data="ABC: Do a thing")):
            return_code = main([f"--additional-commit-codes={additional_code}"])
            self.assertEqual(return_code, 0)

        # Ensure a default code still works.
        with patch("builtins.open", mock_open(read_data="DOC: Update docs")):
            return_code = main([f"--additional-commit-codes={additional_code}"])
            self.assertEqual(return_code, 0)

    def test_with_maximum_header_length_violated(self):
        """Test an error is raised when the specified maximum header length is violated."""
        with patch("builtins.open", mock_open(read_data="FIX: Fix a bug")):
            return_code = main(["--maximum-header-length=1"])

        self.assertEqual(return_code, 1)

    def test_with_valid_header_ending_pattern_violated(self):
        """Test an error is raised when the specified header-ending-pattern is violated."""
        with patch("builtins.open", mock_open(read_data="FIX: Fix a bug")):
            return_code = main(["--valid-header-ending-pattern=@"])

        self.assertEqual(return_code, 1)

    def test_with_require_body_violated(self):
        """Test an error is raised when a body is not provided when it is required."""
        with patch("builtins.open", mock_open(read_data="FIX: Fix a bug")):
            return_code = main(["--require-body=1"])

        self.assertEqual(return_code, 1)

    def test_with_maximum_body_line_length_violated(self):
        """Test an error is raised when the specified maximum body line length is violated."""
        with patch("builtins.open", mock_open(read_data="FIX: Fix a bug\n\nhello")):
            return_code = main(["--maximum-body-line-length=1"])

        self.assertEqual(return_code, 1)
