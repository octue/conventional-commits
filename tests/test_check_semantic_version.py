import unittest
from unittest.mock import patch

from conventional_commits import check_semantic_version


class MockCompletedProcess:
    """A mock of subprocess.CompletedProcess.

    :param bytes stdout:
    :return None:
    """

    def __init__(self, stdout):
        self.stdout = stdout


class TestCheckSemanticVersion(unittest.TestCase):
    def test_get_current_version(self):
        """Test that the current version can be parsed from a successful subprocess command."""
        with patch("subprocess.run", return_value=MockCompletedProcess(stdout=b"0.3.9")):
            version = check_semantic_version.get_current_version("setup.py")
            self.assertEqual(version, "0.3.9")

    def test_get_expected_semantic_version(self):
        """Test that the expected semantic version can be parsed from a successful git-mkver command."""
        with patch("subprocess.run", return_value=MockCompletedProcess(stdout=b"0.3.9")):
            version = check_semantic_version.get_expected_semantic_version()
            self.assertEqual(version, "0.3.9")

    def test_main_with_matching_versions(self):
        """Test that the correct message and error message are returned if the current version and the expected version
        are the same.
        """
        with patch("sys.argv", return_value=["test_check_semantic_version", "setup.py"]):
            with patch(
                "conventional_commits.check_semantic_version.get_expected_semantic_version", return_value="0.3.9"
            ):
                with patch("conventional_commits.check_semantic_version.get_current_version", return_value="0.3.9"):
                    with patch("sys.stdout") as mock_stdout:
                        with self.assertRaises(SystemExit) as e:
                            check_semantic_version.main()

                            # Check that the exit code is 0.
                            self.assertFalse(hasattr(e, "exception"))

                        message = mock_stdout.method_calls[0].args[0]
                        self.assertIn("VERSION PASSED CHECKS:", message)
                        self.assertIn(
                            "The current version is the same as the expected semantic version: 0.3.9.", message
                        )

    def test_main_with_non_matching_versions(self):
        """Test that the correct message and error message are returned if the current version and the expected version
        are not the same.
        """
        with patch("sys.argv", return_value=["test_check_semantic_version", "setup.py"]):
            with patch(
                "conventional_commits.check_semantic_version.get_expected_semantic_version", return_value="0.5.3"
            ):
                with patch("conventional_commits.check_semantic_version.get_current_version", return_value="0.3.9"):
                    with patch("sys.stdout") as mock_stdout:
                        with self.assertRaises(SystemExit) as e:
                            check_semantic_version.main()

                            # Check that the exit code is 1.
                            self.assertEqual(e.exception.code, 1)

                        message = mock_stdout.method_calls[0].args[0]
                        self.assertIn("VERSION FAILED CHECKS:", message)
                        self.assertIn(
                            "The current version (0.3.9) is different from the expected semantic version (0.5.3).",
                            message,
                        )

    def test_main_with_non_matching_versions_reversed(self):
        """Test that the correct message and error message are returned if the current version and the expected version
        are not the same (reversed compared to the previous test).
        """
        with patch("sys.argv", return_value=["test_check_semantic_version", "setup.py"]):
            with patch(
                "conventional_commits.check_semantic_version.get_expected_semantic_version", return_value="0.3.9"
            ):
                with patch("conventional_commits.check_semantic_version.get_current_version", return_value="0.5.3"):
                    with patch("sys.stdout") as mock_stdout:
                        with self.assertRaises(SystemExit) as e:
                            check_semantic_version.main()

                            # Check that the exit code is 1.
                            self.assertEqual(e.exception.code, 1)

                        message = mock_stdout.method_calls[0].args[0]
                        self.assertIn("VERSION FAILED CHECKS:", message)
                        self.assertIn(
                            "The current version (0.5.3) is different from the expected semantic version (0.3.9).",
                            message,
                        )
