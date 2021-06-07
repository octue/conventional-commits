import unittest

from pre_commit_hooks.conventional_commits.checker import ConventionalCommitMessageChecker


class TestCheckCommitMessage(unittest.TestCase):
    def test_empty_commit_message_raises_error(self):
        with self.assertRaises(ValueError):
            ConventionalCommitMessageChecker().check_commit_message([])

    def test_header_but_no_body_when_body_is_required_raises_error(self):
        with self.assertRaises(ValueError):
            ConventionalCommitMessageChecker(require_body=True).check_commit_message(["FIX: Fix this bug"])

    def test_with_header_but_no_body_when_body_is_not_required(self):
        ConventionalCommitMessageChecker().check_commit_message(["FIX: Fix this bug"])

    def test_empty_header_raises_error(self):
        with self.assertRaises(ValueError):
            ConventionalCommitMessageChecker().check_commit_message([""])

    def test_invalid_commit_code_raises_error(self):
        with self.assertRaises(ValueError):
            ConventionalCommitMessageChecker().check_commit_message(["BLAH: This is a blah commit"])

    def test_header_over_maximum_length_raises_error(self):
        with self.assertRaises(ValueError):
            ConventionalCommitMessageChecker().check_commit_message([f"IMP: {'a' * 80}"])

    def test_invalid_header_ending_raises_error(self):
        with self.assertRaises(ValueError):
            ConventionalCommitMessageChecker().check_commit_message(["FIX: Fix this bug."])

    def test_non_blank_header_separator_line_raises_error(self):
        with self.assertRaises(ValueError):
            ConventionalCommitMessageChecker().check_commit_message(["FIX: Fix this bug", "Body started too early."])

    def test_with_body_when_body_not_required(self):
        ConventionalCommitMessageChecker().check_commit_message(["FIX: Fix this bug", "", "This is the body."])

    def test_with_body_when_body_required(self):
        ConventionalCommitMessageChecker(require_body=True).check_commit_message(
            ["FIX: Fix this bug", "", "This is the body."]
        )

    def test_empty_body_raises_error(self):
        with self.assertRaises(ValueError):
            ConventionalCommitMessageChecker(require_body=True).check_commit_message(["FIX: Fix this bug", "", ""])

    def test_body_lines_over_maximum_lenth_raises_error(self):
        with self.assertRaises(ValueError):
            ConventionalCommitMessageChecker(require_body=True).check_commit_message(
                ["FIX: Fix this bug", "", f"{'a' * 80}"]
            )

        with self.assertRaises(ValueError):
            ConventionalCommitMessageChecker(require_body=True).check_commit_message(
                ["FIX: Fix this bug", "", "an okay line", f"{'a' * 80}"]
            )

    def test_comments_lines_are_ignored(self):
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
                "#       modified:   pre_commit_hooks/conventional_commits/checker.py",
                "#       modified:   pre_commit_hooks/tests/test_check_commit_message.py",
                "#",
            ]
        )

    def test_trailing_newline_is_ignored(self):
        ConventionalCommitMessageChecker().check_commit_message(["FIX: Fix this bug", ""])
