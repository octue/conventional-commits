import unittest
from pre_commit_conventional_commit_message.check_commit_message import check_commit_message


class TestCheckCommitMessage(unittest.TestCase):

    def test_empty_commit_message_raises_error(self):
        with self.assertRaises(ValueError):
            check_commit_message([])

    def test_header_but_no_body_when_body_is_required_raises_error(self):
        with self.assertRaises(ValueError):
            check_commit_message(["FIX: Fix this bug"], require_body=True)

    def test_with_header_but_no_body_when_body_is_not_required(self):
        check_commit_message(["FIX: Fix this bug"], require_body=False)

    def test_empty_header_raises_error(self):
        with self.assertRaises(ValueError):
            check_commit_message([""])

    def test_invalid_commit_code_raises_error(self):
        with self.assertRaises(ValueError):
            check_commit_message(["BLAH: This is a blah commit"])

    def test_header_over_maximum_length_raises_error(self):
        with self.assertRaises(ValueError):
            check_commit_message([f"IMP: {'a' * 80}"])

    def test_invalid_header_ending_raises_error(self):
        with self.assertRaises(ValueError):
            check_commit_message(["FIX: Fix this bug."], require_body=False)

    def test_non_blank_header_separator_line_raises_error(self):
        with self.assertRaises(ValueError):
            check_commit_message(["FIX: Fix this bug", "Body started too early."])

    def test_with_body_when_body_not_required(self):
        check_commit_message(["FIX: Fix this bug", "", "This is the body."], require_body=False)

    def test_with_body_when_body_required(self):
        check_commit_message(["FIX: Fix this bug", "", "This is the body."], require_body=True)

    def test_empty_body_raises_error(self):
        with self.assertRaises(ValueError):
            check_commit_message(["FIX: Fix this bug", "", ""], require_body=True)

    def test_body_lines_over_maximum_lenth_raises_error(self):
        with self.assertRaises(ValueError):
            check_commit_message(["FIX: Fix this bug", "", f"{'a' * 80}"], require_body=True)

        with self.assertRaises(ValueError):
            check_commit_message(["FIX: Fix this bug", "", "an okay line", f"{'a' * 80}"], require_body=True)
