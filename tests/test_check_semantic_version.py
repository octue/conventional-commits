import os
import unittest
from unittest.mock import patch

from conventional_commits import check_semantic_version


TEST_DIRECTORY = os.path.abspath(os.path.dirname(__file__))
TEST_DATA_DIRECTORY = os.path.join(TEST_DIRECTORY, "test_package")


class MockCompletedProcess:
    """A mock of subprocess.CompletedProcess.

    :param bytes stdout:
    :return None:
    """

    def __init__(self, stdout):
        self.stdout = stdout


class TestCheckSemanticVersion(unittest.TestCase):
    def test_error_raised_if_unsupported_version_source_provided(self):
        """Ensure an error is raised if an unsupported version source is provided."""
        with self.assertRaises(ValueError):
            check_semantic_version.get_current_version(version_source="blah")

    def test_get_current_version_for_setup_py(self):
        try:
            os.chdir(TEST_DATA_DIRECTORY)
            version = check_semantic_version.get_current_version("setup.py")
            self.assertEqual(version, "0.3.4")
        finally:
            os.chdir(TEST_DIRECTORY)

    def test_get_current_version_with_custom_file_path_for_setup_py(self):
        """Test that the current version can be extracted from a different file than the top-level setup.py file."""
        version = check_semantic_version.get_current_version(
            "setup.py", version_source_file=os.path.join(TEST_DATA_DIRECTORY, "setup.py")
        )

        self.assertEqual(version, "0.3.4")

    def test_get_current_version_for_pyproject_toml(self):
        try:
            os.chdir(TEST_DATA_DIRECTORY)
            version = check_semantic_version.get_current_version("pyproject.toml")
            self.assertEqual(version, "0.6.3")
        finally:
            os.chdir(TEST_DIRECTORY)

    def test_get_current_version_with_custom_file_path_for_pyproject_toml(self):
        """Test that the current version can be extracted from a different file than the top-level file pyproject.toml."""
        version = check_semantic_version.get_current_version(
            "pyproject.toml", version_source_file=os.path.join(TEST_DATA_DIRECTORY, "pyproject.toml")
        )

        self.assertEqual(version, "0.6.3")

    def test_get_current_version_for_package_json(self):
        try:
            os.chdir(TEST_DATA_DIRECTORY)
            version = check_semantic_version.get_current_version("package.json")
            self.assertEqual(version, "1.5.3")
        finally:
            os.chdir(TEST_DIRECTORY)

    def test_get_current_version_with_custom_file_path_for_package_json(self):
        """Test that the current version can be extracted from a different file than the top-level package.json file."""
        version = check_semantic_version.get_current_version(
            "package.json", version_source_file=os.path.join(TEST_DATA_DIRECTORY, "package.json")
        )

        self.assertEqual(version, "1.5.3")

    def test_get_expected_semantic_version(self):
        """Test that the expected semantic version can be parsed from a successful git-mkver command."""
        with patch("subprocess.run", return_value=MockCompletedProcess(stdout=b"0.3.9")):
            version = check_semantic_version.get_expected_semantic_version()
            self.assertEqual(version, "0.3.9")

    def test_main_with_matching_versions(self):
        """Test that the correct message and error message are returned if the current version and the expected version
        are the same.
        """
        with patch("conventional_commits.check_semantic_version.get_expected_semantic_version", return_value="0.3.9"):
            with patch("conventional_commits.check_semantic_version.get_current_version", return_value="0.3.9"):
                with patch("sys.stdout") as mock_stdout:
                    with self.assertRaises(SystemExit) as e:
                        check_semantic_version.main(["setup.py"])

                        # Check that the exit code is 0.
                        self.assertFalse(hasattr(e, "exception"))

                    message = mock_stdout.method_calls[0].args[0]
                    self.assertIn("VERSION PASSED CHECKS:", message)
                    self.assertIn("The current version is the same as the expected semantic version: 0.3.9.", message)

    def test_main_with_non_matching_versions(self):
        """Test that the correct message and error message are returned if the current version and the expected version
        are not the same.
        """
        with patch("conventional_commits.check_semantic_version.get_expected_semantic_version", return_value="0.5.3"):
            with patch("conventional_commits.check_semantic_version.get_current_version", return_value="0.3.9"):
                with patch("sys.stdout") as mock_stdout:
                    with self.assertRaises(SystemExit) as e:
                        check_semantic_version.main(["setup.py"])

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
        with patch("conventional_commits.check_semantic_version.get_expected_semantic_version", return_value="0.3.9"):
            with patch("conventional_commits.check_semantic_version.get_current_version", return_value="0.5.3"):
                with patch("sys.stdout") as mock_stdout:
                    with self.assertRaises(SystemExit) as e:
                        check_semantic_version.main(["setup.py"])

                        # Check that the exit code is 1.
                        self.assertEqual(e.exception.code, 1)

                    message = mock_stdout.method_calls[0].args[0]
                    self.assertIn("VERSION FAILED CHECKS:", message)
                    self.assertIn(
                        "The current version (0.5.3) is different from the expected semantic version (0.3.9).",
                        message,
                    )
