import unittest
from unittest.mock import Mock, patch

from conventional_commits.compile_release_notes import ReleaseNotesCompiler, main


MOCK_GIT_LOG = [
    "3e7dc54|§REF: Merge commit message checker modules|§|§ (HEAD -> refactor/test-release-notes-generator, origin/refactor/test-release-notes-generator)",
    "fabd2ab|§MRG: Merge pull request #3 from octue/feature/add-other-conventional-commit-ci-components|§|§",
    "ef77729|§CHO: Remove hook installation from branch|§|§ (tag: 0.0.3, origin/main, origin/HEAD, main)",
    "b043bc8|§ENH: Support getting versions from poetry and npm|§|§",
    "27dcef0|§FIX: Fix semantic version script; add missing config|§|§",
]

MOCK_PULL_REQUEST_COMMITS = [
    {
        "commit": {
            "message": "MRG: Merge pull request #3 from octue/feature/add-other-conventional-commit-ci-components"
        }
    },
    {"commit": {"message": "ENH: Support getting versions from poetry and npm"}},
    {"commit": {"message": "FIX: Fix semantic version script; add missing config"}},
]

EXPECTED_PULL_REQUEST_START_RELEASE_NOTES_WITH_NON_GENERATED_SECTION = "\n".join(
    [
        "BLAH BLAH BLAH",
        "<!--- START AUTOGENERATED NOTES --->",
        "# Contents",
        "",
        "### Enhancements",
        "- Support getting versions from poetry and npm",
        "",
        "### Fixes",
        "- Fix semantic version script; add missing config",
        "",
        "### Other",
        "- Merge pull request #3 from octue/feature/add-other-conventional-commit-ci-components",
        "",
        "<!--- END AUTOGENERATED NOTES --->",
        "YUM YUM YUM",
    ]
)


class TestReleaseNotesCompiler(unittest.TestCase):
    GIT_LOG_METHOD_PATH = "conventional_commits.compile_release_notes.ReleaseNotesCompiler._get_git_log"
    GET_CURRENT_PULL_REQUEST_PATH = (
        "conventional_commits.compile_release_notes.ReleaseNotesCompiler._get_current_pull_request"
    )
    MOCK_PULL_REQUEST_URL = "https://api.github.com/repos/blah/my-repo/pulls/11"

    def test_unsupported_stop_point_results_in_error(self):
        """Test that using an unsupported stop point results in a ValueError."""
        with self.assertRaises(ValueError):
            ReleaseNotesCompiler(stop_point="blah", pull_request_url="")

    def test_skip_release_notes_auto_generation(self):
        """Test that release notes autogeneration is skipped if the skip indicator is present in the previous notes."""
        previous_notes = (
            "BLAH BLAH BLAH\n<!--- START AUTOGENERATED NOTES --->\n<!--- END AUTOGENERATED NOTES --->YUM YUM YUM"
            "<!--- SKIP AUTOGENERATED NOTES --->"
        )

        with patch(
            self.GET_CURRENT_PULL_REQUEST_PATH,
            return_value={"body": previous_notes, "commits": MOCK_PULL_REQUEST_COMMITS},
        ):
            release_notes = ReleaseNotesCompiler(
                stop_point="PULL_REQUEST_START",
                pull_request_url=self.MOCK_PULL_REQUEST_URL,
                include_link_to_pull_request=False,
            ).compile_release_notes()

        self.assertEqual(release_notes, previous_notes)

    def test_last_release_stop_point(self):
        """Test generating release notes that stop at the last release."""
        with patch(self.GIT_LOG_METHOD_PATH, return_value=MOCK_GIT_LOG):
            release_notes = ReleaseNotesCompiler(
                stop_point="LAST_RELEASE",
                include_link_to_pull_request=False,
            ).compile_release_notes()

        expected = "\n".join(
            [
                "<!--- START AUTOGENERATED NOTES --->",
                "# Contents",
                "",
                "### Refactoring",
                "- Merge commit message checker modules",
                "",
                "### Other",
                "- Merge pull request #3 from octue/feature/add-other-conventional-commit-ci-components",
                "",
                "<!--- END AUTOGENERATED NOTES --->",
            ]
        )

        self.assertEqual(release_notes, expected)

    def test_with_previous_release_notes_missing_autogeneration_markers(self):
        """Test that previous release notes are not overwritten when the autogeneration markers are missing."""
        with patch(
            self.GET_CURRENT_PULL_REQUEST_PATH,
            return_value={"body": "BLAH BLAH BLAH", "commits": MOCK_PULL_REQUEST_COMMITS},
        ):
            release_notes = ReleaseNotesCompiler(
                stop_point="PULL_REQUEST_START",
                pull_request_url=self.MOCK_PULL_REQUEST_URL,
                include_link_to_pull_request=False,
            ).compile_release_notes()

        expected = "\n".join(
            [
                "BLAH BLAH BLAH",
                "<!--- START AUTOGENERATED NOTES --->",
                "# Contents",
                "",
                "### Enhancements",
                "- Support getting versions from poetry and npm",
                "",
                "### Fixes",
                "- Fix semantic version script; add missing config",
                "",
                "### Other",
                "- Merge pull request #3 from octue/feature/add-other-conventional-commit-ci-components",
                "",
                "<!--- END AUTOGENERATED NOTES --->",
            ]
        )

        self.assertEqual(release_notes, expected)

    def test_with_previous_release_notes_with_empty_autogenerated_section(self):
        """Test that text outside the autogeneration markers in previous release notes is not overwritten when the
        autogenerated section is empty.
        """
        previous_notes = (
            "BLAH BLAH BLAH\n<!--- START AUTOGENERATED NOTES --->\n<!--- END AUTOGENERATED NOTES --->YUM YUM YUM"
        )

        with patch(
            self.GET_CURRENT_PULL_REQUEST_PATH,
            return_value={"body": previous_notes, "commits": MOCK_PULL_REQUEST_COMMITS},
        ):
            release_notes = ReleaseNotesCompiler(
                stop_point="PULL_REQUEST_START",
                pull_request_url=self.MOCK_PULL_REQUEST_URL,
                include_link_to_pull_request=False,
            ).compile_release_notes()

        self.assertEqual(release_notes, EXPECTED_PULL_REQUEST_START_RELEASE_NOTES_WITH_NON_GENERATED_SECTION)

    def test_with_previous_release_notes_with_other_text_on_autogeneration_markers_lines(self):
        """Test that text outside but on the same line as the autogeneration markers in previous release notes is not
        overwritten when the autogenerated section is empty.
        """
        previous_notes = (
            "BLAH BLAH BLAH<!--- START AUTOGENERATED NOTES --->\n<!--- END AUTOGENERATED NOTES --->YUM YUM YUM"
        )

        with patch(
            self.GET_CURRENT_PULL_REQUEST_PATH,
            return_value={"body": previous_notes, "commits": MOCK_PULL_REQUEST_COMMITS},
        ):
            release_notes = ReleaseNotesCompiler(
                stop_point="PULL_REQUEST_START",
                pull_request_url=self.MOCK_PULL_REQUEST_URL,
                include_link_to_pull_request=False,
            ).compile_release_notes()

        self.assertEqual(release_notes, EXPECTED_PULL_REQUEST_START_RELEASE_NOTES_WITH_NON_GENERATED_SECTION)

    def test_autogenerated_section_gets_overwritten(self):
        """Test that text enclosed by the autogeneration markers is overwritten."""
        previous_notes = (
            "<!--- START AUTOGENERATED NOTES --->\nBAM BAM BAM\nWAM WAM WAM\n<!--- END AUTOGENERATED NOTES --->"
        )

        with patch(
            self.GET_CURRENT_PULL_REQUEST_PATH,
            return_value={"body": previous_notes, "commits": MOCK_PULL_REQUEST_COMMITS},
        ):
            release_notes = ReleaseNotesCompiler(
                stop_point="PULL_REQUEST_START",
                pull_request_url=self.MOCK_PULL_REQUEST_URL,
                include_link_to_pull_request=False,
            ).compile_release_notes()

        expected = "\n".join(
            [
                "<!--- START AUTOGENERATED NOTES --->",
                "# Contents",
                "",
                "### Enhancements",
                "- Support getting versions from poetry and npm",
                "",
                "### Fixes",
                "- Fix semantic version script; add missing config",
                "",
                "### Other",
                "- Merge pull request #3 from octue/feature/add-other-conventional-commit-ci-components",
                "",
                "<!--- END AUTOGENERATED NOTES --->",
            ]
        )

        self.assertEqual(release_notes, expected)

    def test_autogenerated_section_gets_overwritten_but_text_outside_does_not(self):
        """Test that text outside a non-empty autogenerated section is not overwritten."""
        previous_notes = (
            "BLAH BLAH BLAH\n<!--- START AUTOGENERATED NOTES --->\nBAM BAM BAM<!--- END AUTOGENERATED NOTES --->YUM "
            "YUM YUM"
        )

        with patch(
            self.GET_CURRENT_PULL_REQUEST_PATH,
            return_value={"body": previous_notes, "commits": MOCK_PULL_REQUEST_COMMITS},
        ):
            release_notes = ReleaseNotesCompiler(
                stop_point="PULL_REQUEST_START",
                pull_request_url=self.MOCK_PULL_REQUEST_URL,
                include_link_to_pull_request=False,
            ).compile_release_notes()

        self.assertEqual(release_notes, EXPECTED_PULL_REQUEST_START_RELEASE_NOTES_WITH_NON_GENERATED_SECTION)

    def test_commit_messages_in_non_standard_format_are_left_uncategorised(self):
        """Test that commit messages in a non-standard format are put under an uncategorised heading."""
        mock_git_log = ["fabd2ab|§This is not in the right format|§|§", "27dcef0|§FIX: Fix a bug|§|§"]

        with patch(self.GIT_LOG_METHOD_PATH, return_value=mock_git_log):
            release_notes = ReleaseNotesCompiler(stop_point="LAST_RELEASE").compile_release_notes()

        expected = "\n".join(
            [
                "<!--- START AUTOGENERATED NOTES --->",
                "# Contents",
                "",
                "### Fixes",
                "- Fix a bug",
                "",
                "### Uncategorised!",
                "- This is not in the right format",
                "",
                "<!--- END AUTOGENERATED NOTES --->",
            ]
        )

        self.assertEqual(release_notes, expected)

    def test_commit_messages_with_unrecognised_commit_codes_are_categorised_as_other(self):
        """Test that commit messages with an unrecognised commit code are categorised under "other"."""
        mock_git_log = [
            "27dcef0|§BAM: An unrecognised commit code|§|§",
            "fabd2ab|§FIX: Fix a bug|§|§",
            "cabd2ab|§STY: Apply PEP8 styling|§|§",
        ]

        with patch(self.GIT_LOG_METHOD_PATH, return_value=mock_git_log):
            release_notes = ReleaseNotesCompiler(stop_point="LAST_RELEASE").compile_release_notes()

        expected = "\n".join(
            [
                "<!--- START AUTOGENERATED NOTES --->",
                "# Contents",
                "",
                "### Fixes",
                "- Fix a bug",
                "",
                "### Style",
                "- Apply PEP8 styling",
                "",
                "### Other",
                "- An unrecognised commit code",
                "",
                "<!--- END AUTOGENERATED NOTES --->",
            ]
        )

        self.assertEqual(release_notes, expected)

    def test_updating_release_notes_works_and_does_not_add_extra_newlines_after_autogenerated_section(self):
        """Test that updating release notes that were produced by the release notes compiler previously works (i.e. the
        new commits are categorised and formatted properly) and does not add extra newlines under the autogenerated
        section.
        """
        previous_notes = (
            "BLAH BLAH BLAH\n<!--- START AUTOGENERATED NOTES ---><!--- END AUTOGENERATED NOTES --->YUM YUM YUM"
        )

        with patch(
            self.GET_CURRENT_PULL_REQUEST_PATH,
            return_value={"body": previous_notes, "commits": MOCK_PULL_REQUEST_COMMITS},
        ):
            release_notes_1 = ReleaseNotesCompiler(
                stop_point="PULL_REQUEST_START",
                pull_request_url=self.MOCK_PULL_REQUEST_URL,
                include_link_to_pull_request=False,
            ).compile_release_notes()

        # Add a new commit to the git log.
        updated_pull_request_commits = [{"commit": {"message": "FIX: Fix a bug"}}] + MOCK_PULL_REQUEST_COMMITS

        # Run the compiler on the new git log to update the previous set of release notes.
        with patch(
            self.GET_CURRENT_PULL_REQUEST_PATH,
            return_value={"body": release_notes_1, "commits": updated_pull_request_commits},
        ):
            release_notes_2 = ReleaseNotesCompiler(
                stop_point="PULL_REQUEST_START",
                pull_request_url=self.MOCK_PULL_REQUEST_URL,
                include_link_to_pull_request=False,
            ).compile_release_notes()

        expected = "\n".join(
            [
                "BLAH BLAH BLAH",
                "<!--- START AUTOGENERATED NOTES --->",
                "# Contents",
                "",
                "### Enhancements",
                "- Support getting versions from poetry and npm",
                "",
                "### Fixes",
                "- Fix a bug",
                "- Fix semantic version script; add missing config",
                "",
                "### Other",
                "- Merge pull request #3 from octue/feature/add-other-conventional-commit-ci-components",
                "",
                "<!--- END AUTOGENERATED NOTES --->",
                "YUM YUM YUM",
            ]
        )

        self.assertEqual(release_notes_2, expected)

    def test_last_release_stop_point_is_respected_even_if_tagged_commit_has_no_commit_code(self):
        """Test that the `LAST_RELEASE` stop point is still respected even if the tagged commit (usually a merge commit
        made on GitHub that isn't subject to the Conventional Commits pre-commit check that we use locally) has no
        commit code.
        """
        mock_git_log = [
            "3e7dc54|§OPS: Update mkver.conf to correct pattern|§|§ (HEAD -> develop/issue-wq-521-turbine-prevailing-direction, origin/develop/issue-wq-521-turbine-prevailing-direction)",
            "fabd2ab|§OPS: Update conventional commit version in python-ci|§|§",
            "ef77729|§DOC: update readme for new pre-commit ops|§|§",
            "b043bc8|§OPS: update pull request workflow updated|§|§",
            "27dcef0|§DEP: Version bump to 0.1.0|§|§",
            "358ffd5|§OPS: Delete repo issue and pr template|§|§",
            "44927c6|§OPS: Precommit config updated to use conventional commit|§|§",
            "6589a8e|§CHO: Add _mocks file with the mocked classes|§|§",
            "7cdc980|§ENH: Windmap file inputs format now supports space separated headers|§|§",
            "741bb8d|§ENH: Add prevailing_wind_direction to twine file output schema|§|§",
            "27092a4|§ENH: Handle edge case when wind dir not in the data and WD_<whatever> in the time series file. Add tests for checking for None prevailing wind directions|§|§",
            "6dcdc41|§ENH: Mast prevailing wind direction happens when each mast time series file is imported instead of in every turbine|§|§",
            "b69e7e1|§FEA: Add turbine prevailing wind direction to the result as a property of turbine|§|§",
            "0b20f41|§CHO: Clear up the comments and add logging|§|§",
            "05ec990|§CHORE: Remove unused test|§|§",
            "e506bb4|§ENH: The prevailing wind calculation now de-seasons the count of the bins and determines the prevailing wind direction. Slow as *|§|§",
            "9c125ab|§FEAT: Added a utility module which calculates the prevailing wind direction given a wind direction time series|§|§",
            "3d981b6|§Merge pull request #103 from windpioneers/release/0.0.11|§|§ (tag: 0.0.11, origin/main, main)",
            "9b88bc6|§ENH: Added an assert to bring the coverage up|§|§",
            "17d8de1|§ENH: Remove a json turbine data importer, we are not going to be importing a turbine from json 'cos we use pcu for that|§|§",
            "d242271|§DEP: Update pcu version to 0.0.6|§|§",
        ]

        with patch(self.GIT_LOG_METHOD_PATH, return_value=mock_git_log):
            release_notes = ReleaseNotesCompiler(
                stop_point="LAST_RELEASE", include_link_to_pull_request=False
            ).compile_release_notes()

        expected_release_notes = "\n".join(
            [
                "<!--- START AUTOGENERATED NOTES --->",
                "# Contents",
                "",
                "### New features",
                "- Add turbine prevailing wind direction to the result as a property of turbine",
                "",
                "### Enhancements",
                "- Windmap file inputs format now supports space separated headers",
                "- Add prevailing_wind_direction to twine file output schema",
                "- Handle edge case when wind dir not in the data and WD_<whatever> in the time series file. Add tests for checking for None prevailing wind directions",
                "- Mast prevailing wind direction happens when each mast time series file is imported instead of in every turbine",
                "- The prevailing wind calculation now de-seasons the count of the bins and determines the prevailing wind direction. Slow as *",
                "",
                "### Operations",
                "- Update mkver.conf to correct pattern",
                "- Update conventional commit version in python-ci",
                "- update pull request workflow updated",
                "- Delete repo issue and pr template",
                "- Precommit config updated to use conventional commit",
                "",
                "### Dependencies",
                "- Version bump to 0.1.0",
                "",
                "### Chores",
                "- Add _mocks file with the mocked classes",
                "- Clear up the comments and add logging",
                "",
                "### Other",
                "- update readme for new pre-commit ops",
                "- Remove unused test",
                "- Added a utility module which calculates the prevailing wind direction given a wind direction time series",
                "",
                "<!--- END AUTOGENERATED NOTES --->",
            ]
        )

        self.assertEqual(release_notes, expected_release_notes)

    def test_commit_message_with_extra_colons_are_still_categorised(self):
        """Test that commit headers containing extra colons in addition to the colon splitting the commit code from the
        rest of the commit header are still categorised correctly.
        """
        mock_git_log = [
            "3e7dc54|§OPS: My message: something|§|§",
            "fabd2ab|§OPS: Update conventional commit version in python-ci|§|§",
        ]

        with patch(self.GIT_LOG_METHOD_PATH, return_value=mock_git_log):
            release_notes = ReleaseNotesCompiler(
                stop_point="LAST_RELEASE", include_link_to_pull_request=False
            ).compile_release_notes()

        expected_release_notes = "\n".join(
            [
                "<!--- START AUTOGENERATED NOTES --->",
                "# Contents",
                "",
                "### Operations",
                "- My message: something",
                "- Update conventional commit version in python-ci",
                "",
                "<!--- END AUTOGENERATED NOTES --->",
            ]
        )
        self.assertEqual(release_notes, expected_release_notes)

    def test_commit_hash_merges_are_ignored(self):
        """Ensure commit messages that are just a merge of a commit ref into another commit ref are ignored."""
        mock_git_log = [
            "3e7dc54|§OPS: My message: something|§|§",
            "fabd2ab|§Merge ef777290453f11b7519dbd3410b01d34d2e13566 into b043bc85cf558f1706188fafe9676ecd0642ab5a|§|§",
            "ef77729|§OPS: Update conventional commit version in python-ci|§|§",
        ]

        with patch(self.GIT_LOG_METHOD_PATH, return_value=mock_git_log):
            release_notes = ReleaseNotesCompiler(
                stop_point="LAST_RELEASE", include_link_to_pull_request=False
            ).compile_release_notes()

        expected_release_notes = "\n".join(
            [
                "<!--- START AUTOGENERATED NOTES --->",
                "# Contents",
                "",
                "### Operations",
                "- My message: something",
                "- Update conventional commit version in python-ci",
                "",
                "<!--- END AUTOGENERATED NOTES --->",
            ]
        )
        self.assertEqual(release_notes, expected_release_notes)

    def test_single_breaking_change_is_indicated(self):
        """Test that a single breaking change is indicated in the release notes at the top and next to the categorised
        commit message.
        """
        mock_git_log = ["fabd2ab|§ENH: Make big change|§BREAKING CHANGE: blah blah blah|§"] + MOCK_GIT_LOG

        with patch(self.GIT_LOG_METHOD_PATH, return_value=mock_git_log):
            release_notes = ReleaseNotesCompiler(
                stop_point="LAST_RELEASE", include_link_to_pull_request=False
            ).compile_release_notes()

        self.assertEqual(
            release_notes,
            "\n".join(
                [
                    "<!--- START AUTOGENERATED NOTES --->",
                    "# Contents",
                    "",
                    "**IMPORTANT:** There is 1 breaking change.",
                    "",
                    "### Enhancements",
                    "- 💥 **BREAKING CHANGE:** Make big change",
                    "",
                    "### Refactoring",
                    "- Merge commit message checker modules",
                    "",
                    "### Other",
                    "- Merge pull request #3 from octue/feature/add-other-conventional-commit-ci-components",
                    "",
                    "---",
                    "# Upgrade instructions",
                    "<details>",
                    "<summary>💥 <b>Make big change</b></summary>",
                    "",
                    "blah blah blah",
                    "</details>",
                    "",
                    "<!--- END AUTOGENERATED NOTES --->",
                ]
            ),
        )

    def test_multiple_breaking_changes_are_indicated(self):
        """Test that multiple breaking changes are indicated in the release notes at the top and next to the categorised
        commit message.
        """
        mock_git_log = [
            "fabd2ab|§ENH: Make big change|§BREAKING-CHANGE: blah blah blah|§",
            "fabd2ab|§FIX: Make breaking fix|§BREAKING CHANGE: How to update\n- Point\n- Another point\n\nSome text|§",
            "fabd2ab|§REF: Change interface|§BREAKING-CHANGE: glob|§",
        ] + MOCK_GIT_LOG

        with patch(self.GIT_LOG_METHOD_PATH, return_value=mock_git_log):
            release_notes = ReleaseNotesCompiler(
                stop_point="LAST_RELEASE", include_link_to_pull_request=False
            ).compile_release_notes()

        self.assertEqual(
            release_notes,
            "\n".join(
                [
                    "<!--- START AUTOGENERATED NOTES --->",
                    "# Contents",
                    "",
                    "**IMPORTANT:** There are 3 breaking changes.",
                    "",
                    "### Enhancements",
                    "- 💥 **BREAKING CHANGE:** Make big change",
                    "",
                    "### Fixes",
                    "- 💥 **BREAKING CHANGE:** Make breaking fix",
                    "",
                    "### Refactoring",
                    "- 💥 **BREAKING CHANGE:** Change interface",
                    "- Merge commit message checker modules",
                    "",
                    "### Other",
                    "- Merge pull request #3 from octue/feature/add-other-conventional-commit-ci-components",
                    "",
                    "---",
                    "# Upgrade instructions",
                    "<details>",
                    "<summary>💥 <b>Make big change</b></summary>",
                    "",
                    "blah blah blah",
                    "</details>",
                    "",
                    "<details>",
                    "<summary>💥 <b>Make breaking fix</b></summary>",
                    "",
                    "How to update",
                    "- Point",
                    "- Another point",
                    "",
                    "Some text",
                    "</details>",
                    "",
                    "<details>",
                    "<summary>💥 <b>Change interface</b></summary>",
                    "",
                    "glob",
                    "</details>",
                    "",
                    "<!--- END AUTOGENERATED NOTES --->",
                ]
            ),
        )

    def test_commit_messages_with_multi_line_bodies(self):
        """Test that commits with multi-line bodies work with the release notes compiler."""
        mock_git_log = ["fabd2ab|§ENH: Blah blah|§This is the body.\n Here is another body line|§"] + MOCK_GIT_LOG

        with patch(self.GIT_LOG_METHOD_PATH, return_value=mock_git_log):
            release_notes = ReleaseNotesCompiler(
                stop_point="LAST_RELEASE", include_link_to_pull_request=False
            ).compile_release_notes()

        expected = "\n".join(
            [
                "<!--- START AUTOGENERATED NOTES --->",
                "# Contents",
                "",
                "### Enhancements",
                "- Blah blah",
                "",
                "### Refactoring",
                "- Merge commit message checker modules",
                "",
                "### Other",
                "- Merge pull request #3 from octue/feature/add-other-conventional-commit-ci-components",
                "",
                "<!--- END AUTOGENERATED NOTES --->",
            ]
        )

        self.assertEqual(release_notes, expected)

    def test_include_link_to_pull_request(self):
        """Test that the HTML URL of the pull request is included in the release notes if requested."""
        html_url = "https://github.com/octue/conventional-commits/pull/40"

        with patch(
            self.GET_CURRENT_PULL_REQUEST_PATH,
            return_value={"body": "", "number": 40, "html_url": html_url, "commits": MOCK_PULL_REQUEST_COMMITS},
        ):
            release_notes = ReleaseNotesCompiler(
                stop_point="PULL_REQUEST_START",
                pull_request_url="https://api.github.com/repos/octue/conventional-commits/pulls/40",
                include_link_to_pull_request=True,
            ).compile_release_notes()

        expected = "\n".join(
            [
                "<!--- START AUTOGENERATED NOTES --->",
                "# Contents ([#40](https://github.com/octue/conventional-commits/pull/40))",
                "",
                "### Enhancements",
                "- Support getting versions from poetry and npm",
                "",
                "### Fixes",
                "- Fix semantic version script; add missing config",
                "",
                "### Other",
                "- Merge pull request #3 from octue/feature/add-other-conventional-commit-ci-components",
                "",
                "<!--- END AUTOGENERATED NOTES --->",
            ]
        )

        self.assertEqual(release_notes, expected)

    def test_last_release_stop_point_used_if_pull_request_is_not_accessible(self):
        """Test that a warning is logged and the LAST_RELEASE stop point is used if the given pull request isn't
        accessible.
        """
        with patch(self.GIT_LOG_METHOD_PATH, return_value=MOCK_GIT_LOG):
            with patch("requests.get", return_value=Mock(status_code=404)):
                with self.assertLogs() as logging_context:
                    compiler = ReleaseNotesCompiler(
                        stop_point="PULL_REQUEST_START",
                        pull_request_url="https://api.github.com/repos/octue/conventional-commits/pulls/40",
                        include_link_to_pull_request=True,
                    )

                    self.assertEqual(logging_context.records[0].levelname, "WARNING")
                    self.assertEqual(logging_context.records[2].message, "Using 'LAST_RELEASE' stop point.")

            compiler.compile_release_notes()

        self.assertEqual(compiler.stop_point, "LAST_RELEASE")

    def test_get_pull_request_with_api_token(self):
        """Test that a pull request can be accessed using a GitHub API token."""
        pull_request_url = "https://api.github.com/repos/octue/conventional-commits/pulls/40"

        with patch(
            "requests.get",
            return_value=Mock(
                status_code=200, json=lambda: {"body": "blah", "commits_url": "https://url/to/commits"}, links={}
            ),
        ) as mock_get:
            compiler = ReleaseNotesCompiler(
                stop_point="PULL_REQUEST_START",
                pull_request_url=pull_request_url,
                api_token="blah",
            )

        # Check the pull request URL has been requested.
        self.assertEqual(mock_get.call_args_list[0].args, (pull_request_url,))
        self.assertEqual(mock_get.call_args_list[0].kwargs, {"headers": {"Authorization": "token blah"}})

        # Check the commits URL has been requested and the returned JSON added to the pull request JSON.
        self.assertEqual(mock_get.call_args_list[1].args, ("https://url/to/commits?per_page=100",))
        self.assertIn("commits", compiler.current_pull_request)


class TestMain(unittest.TestCase):
    def test_cli_with_no_link_to_pull_request(self):
        """Test that the CLI passes its arguments to the release notes compiler correctly when the
        `--no-link-to-pull-request` flag is present.
        """
        with patch("conventional_commits.compile_release_notes.ReleaseNotesCompiler") as mock_compiler:
            main(
                [
                    "LAST_RELEASE",
                    "--pull-request-url=https://github.com/blah/blah/pulls/32",
                    "--api-token=github-token",
                    "--header=# My heading",
                    "--list-item-symbol=-",
                    "--no-link-to-pull-request",
                ]
            )

        mock_compiler.assert_called_with(
            stop_point="LAST_RELEASE",
            pull_request_url="https://github.com/blah/blah/pulls/32",
            api_token="github-token",
            header="# My heading",
            list_item_symbol="-",
            include_link_to_pull_request=False,
        )

    def test_cli_with_link_to_pull_request(self):
        """Test that the CLI passes its arguments to the release notes compiler correctly when the
        `--no-link-to-pull-request` flag is absent.
        """
        with patch("conventional_commits.compile_release_notes.ReleaseNotesCompiler") as mock_compiler:
            main(
                [
                    "LAST_RELEASE",
                    "--pull-request-url=https://github.com/blah/blah/pulls/32",
                    "--api-token=github-token",
                    "--header=# My heading",
                    "--list-item-symbol=-",
                ]
            )

        mock_compiler.assert_called_with(
            stop_point="LAST_RELEASE",
            pull_request_url="https://github.com/blah/blah/pulls/32",
            api_token="github-token",
            header="# My heading",
            list_item_symbol="-",
            include_link_to_pull_request=True,
        )
