import unittest

from conventional_commits.commit_message_checker import ConventionalCommitMessageChecker


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
        with self.assertRaises(ValueError):
            ConventionalCommitMessageChecker(require_body=True).check_commit_message(
                ["FIX: Fix this bug", "", f"{'a' * 80}"]
            )

        with self.assertRaises(ValueError):
            ConventionalCommitMessageChecker(require_body=True).check_commit_message(
                ["FIX: Fix this bug", "", "an okay line", f"{'a' * 80}"]
            )

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
                "#       modified:   conventional-commits/commit_message_checker.py",
                "#       modified:   tests/test_checker.py",
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
