import argparse
import logging
import re
import subprocess

import requests

from conventional_commits.check_commit_message import (
    BREAKING_CHANGE_INDICATORS as CONVENTIONAL_COMMIT_BREAKING_CHANGE_INDICATORS,
)


logger = logging.getLogger(__name__)


LAST_RELEASE = "LAST_RELEASE"
PULL_REQUEST_START = "PULL_REQUEST_START"
STOP_POINTS = (LAST_RELEASE, PULL_REQUEST_START)

BREAKING_CHANGE_INDICATOR = "**BREAKING CHANGE:** "

COMMIT_REF_MERGE_PATTERN = re.compile(r"Merge [0-9a-f]+ into [0-9a-f]+")
SEMANTIC_VERSION_PATTERN = re.compile(r"tag: (\d+\.\d+\.\d+)")

COMMIT_CODES_TO_HEADINGS_MAPPING = {
    "FEA": "### New features",
    "ENH": "### Enhancements",
    "FIX": "### Fixes",
    "OPS": "### Operations",
    "DEP": "### Dependencies",
    "REF": "### Refactoring",
    "TST": "### Testing",
    "MRG": "### Other",
    "REV": "### Reversions",
    "CHO": "### Chores",
    "WIP": "### Other",
    "DOC": "### Other",
    "STY": "### Other",
}

BREAKING_CHANGE_COUNT_KEY = "BREAKING CHANGE COUNT"

AUTO_GENERATION_START_INDICATOR = "<!--- START AUTOGENERATED NOTES --->"
AUTO_GENERATION_END_INDICATOR = "<!--- END AUTOGENERATED NOTES --->"
SKIP_INDICATOR = "<!--- SKIP AUTOGENERATED NOTES --->"


class ReleaseNotesCompiler:
    """A release/pull request notes compiler. The notes are pulled together from Conventional Commit messages, stopping
    at the specified stop point. The stop point can either be the last merged pull request in the branch or the last
    semantically-versioned release tagged in the branch. If previous notes are provided, only the text between the
    comment lines `<!--- START AUTOGENERATED NOTES --->` and `<!--- END AUTOGENERATED NOTES --->` will be replaced -
    anything outside of this will appear in the new release notes.

    :param str stop_point: the point in the git history up to which commit messages should be used - should be either "LAST_RELEASE" or "PULL_REQUEST_START"
    :param str|None pull_request_url: GitHub API URL for the pull request - this can be accessed in a GitHub workflow as ${{ github.event.pull_request.url }}
    :param str|None api_token: GitHub API token - this can be accessed in a GitHub workflow as ${{ secrets.GITHUB_TOKEN }}
    :param str header: the header to put above the autogenerated release notes, including any markdown styling (defaults to "## Contents")
    :param str list_item_symbol: the markdown symbol to use for listing the commit messages in the release notes (defaults to a ticked checkbox but could be a bullet point or number)
    :param dict|None commit_codes_to_headings_mapping: mapping of commit codes to the header they should be put under, including markdown styling (e.g. "### Fixes")
    :param bool include_link_to_pull_request: if `True`, link to the given pull request in the release notes; ignore if no pull request URL is given
    :return None:
    """

    def __init__(
        self,
        stop_point,
        pull_request_url=None,
        api_token=None,
        header="## Contents",
        list_item_symbol="-",
        commit_codes_to_headings_mapping=None,
        include_link_to_pull_request=True,
    ):
        if stop_point.upper() not in STOP_POINTS:
            raise ValueError(f"`stop_point` must be one of {STOP_POINTS!r}; received {stop_point!r}.")

        self.stop_point = stop_point.upper()

        self.current_pull_request = None
        self.previous_notes = None

        if pull_request_url:
            self.current_pull_request = self._get_current_pull_request(pull_request_url, api_token)

            if self.current_pull_request:
                self.previous_notes = self.current_pull_request["body"]

        self.header = header
        self.list_item_symbol = list_item_symbol
        self.commit_codes_to_headings_mapping = commit_codes_to_headings_mapping or COMMIT_CODES_TO_HEADINGS_MAPPING
        self.include_link_to_pull_request = include_link_to_pull_request

        logger.info(f"Using {self.stop_point!r} stop point.")

    def compile_release_notes(self):
        """Compile the commit messages since the given stop point into a new set of release notes, sorting them into
        headed sections according to their commit codes via the commit-codes-to-headings mapping. If the previous set
        of release notes have been provided then:

        * If the skip indicator is present, the previous notes are returned as they are
        * Otherwise if the autogeneration indicators are present, the previous notes are left unchanged apart from
          between these indicators, where the new autogenerated release notes overwrite whatever was between them before
        * If the autogeneration indicators are not present, the new autogenerated release notes are added after the
          previous notes

        :return str:
        """
        if self.previous_notes and SKIP_INDICATOR in self.previous_notes:
            return self.previous_notes

        if self.current_pull_request:
            parsed_commits, unparsed_commits = self._parse_commit_messages_from_github()
        else:
            parsed_commits, unparsed_commits = self._parse_commit_messages_from_git_log()

        categorised_commit_messages = self._categorise_commit_messages(parsed_commits, unparsed_commits)
        autogenerated_release_notes = self._build_release_notes(categorised_commit_messages)

        if not self.previous_notes:
            return autogenerated_release_notes

        previous_notes_before_generated_section = self.previous_notes.split(AUTO_GENERATION_START_INDICATOR)
        previous_notes_after_generated_section = "".join(previous_notes_before_generated_section[1:]).split(
            AUTO_GENERATION_END_INDICATOR
        )

        return "\n".join(
            (
                previous_notes_before_generated_section[0].strip("\n"),
                autogenerated_release_notes,
                previous_notes_after_generated_section[-1].strip("\n"),
            )
        ).strip('"\n')

    def _get_current_pull_request(self, pull_request_url, api_token):
        """Get the current pull request from the GitHub API.

        :param str pull_request_url: the GitHub API URL for the pull request
        :param str|None api_token: GitHub API token
        :return dict|None:
        """
        if api_token is None:
            headers = {}
        else:
            headers = {"Authorization": f"token {api_token}"}

        response = requests.get(pull_request_url, headers=headers)

        if response.status_code == 200:
            pull_request = response.json()
            pull_request["commits"] = requests.get(self.current_pull_request["commits_url"], headers=headers).json()
            return pull_request

        logger.warning(
            f"Pull request could not be accessed; resorting to using {LAST_RELEASE} stop point.\n"
            f"{response.status_code}: {response.text}."
        )

        self.stop_point = LAST_RELEASE
        return None

    def _get_git_log(self):
        """Get the one-line decorated git log formatted in the pattern of "hash|§header|§body|§decoration@@@".

        Explanation:
        * "|§" delimits the hash from the header, the header from the potentially multi-line body, and the body from the
          decoration
        * "@@@" indicates the end of the git log line. "\n" cannot be used as commit bodies can contain newlines, so
        they can't be used by themselves to delimit git log entries.
        * The specific characters used for the delimiters have been chosen so that they are very uncommon to reduce
          delimiting errors

        :return list(str):
        """
        return (
            subprocess.run(["git", "log", "--pretty=format:%h|§%s|§%b|§%d@@@"], capture_output=True)
            .stdout.strip()
            .decode()
        ).split("@@@")

    def _parse_commit_messages_from_git_log(self):
        """Parse commit messages from the git log (formatted using `--pretty=format:%h|§%s|§%b|§%d@@@`) until the stop
        point is reached. The parsed commit messages are returned separately to any that fail to parse.

        :return list(tuple), list(str):
        """
        parsed_commits = []
        unparsed_commits = []

        for commit in self._get_git_log():
            hash, header, body, decoration = commit.split("|§")

            if "tag" in decoration:
                if bool(SEMANTIC_VERSION_PATTERN.search(decoration)):
                    break

            # A colon separating the commit code from the commit header is required - keep commit messages that
            # don't conform to this but put them into an unparsed category. Ignore commits that are merges of one
            # commit ref into another (GitHub Actions produces these - they don't appear in the actual history of
            # the branch so can be safely ignored when making release notes).
            if ":" not in header:
                if not COMMIT_REF_MERGE_PATTERN.search(header):
                    unparsed_commits.append(header.strip())
                continue

            # Allow commit headers with extra colons.
            code, *header = header.split(":")
            header = ":".join(header)

            parsed_commits.append((code.strip(), header.strip(), body.strip()))

        return parsed_commits, unparsed_commits

    def _parse_commit_messages_from_github(self):
        """Parse commit messages from the GitHub pull request. The parsed commit messages are returned separately to
        any that fail to parse.

        :return list(tuple), list(str):
        """
        parsed_commits = []
        unparsed_commits = []

        for commit in self.current_pull_request["commits"]:
            header, *body = commit["commit"]["message"].split("\n")
            body = "\n".join(body)

            # A colon separating the commit code from the commit header is required - keep commit messages that
            # don't conform to this but put them into an unparsed category. Ignore commits that are merges of one
            # commit ref into another (GitHub Actions produces these - they don't appear in the actual history of
            # the branch so can be safely ignored when making release notes).
            if ":" not in header:
                if not COMMIT_REF_MERGE_PATTERN.search(header):
                    unparsed_commits.append(header.strip())
                continue

            # Allow commit headers with extra colons.
            code, *header = header.split(":")
            header = ":".join(header)

            parsed_commits.append((code.strip(), header.strip(), body.strip()))

        return parsed_commits, unparsed_commits

    def _categorise_commit_messages(self, parsed_commits, unparsed_commits):
        """Categorise the commit messages into headed sections. Unparsed commits are put under an "uncategorised"
        header.

        :param iter(tuple)) parsed_commits:
        :param iter(str) unparsed_commits:
        :return dict:
        """
        release_notes = {heading: [] for heading in self.commit_codes_to_headings_mapping.values()}
        release_notes[BREAKING_CHANGE_COUNT_KEY] = 0

        for code, header, body in parsed_commits:
            try:
                if any(indicator in body for indicator in CONVENTIONAL_COMMIT_BREAKING_CHANGE_INDICATORS):
                    commit_note = BREAKING_CHANGE_INDICATOR + header
                    release_notes[BREAKING_CHANGE_COUNT_KEY] += 1
                else:
                    commit_note = header

                release_notes[self.commit_codes_to_headings_mapping[code]].append(commit_note)

            except KeyError:
                release_notes["### Other"].append(header)

        release_notes["### Uncategorised!"] = unparsed_commits
        return release_notes

    def _build_release_notes(self, categorised_commit_messages):
        """Build the the categorised commit messages into a single multi-line string ready to be used as formatted
        release notes.

        :param dict categorised_commit_messages:
        :return str:
        """
        if self.current_pull_request is not None and self.include_link_to_pull_request:
            link_to_pull_request = (
                f" ([#{self.current_pull_request['number']}]({self.current_pull_request['html_url']}))"
            )
        else:
            link_to_pull_request = ""

        release_notes_for_printing = f"{AUTO_GENERATION_START_INDICATOR}\n{self.header}{link_to_pull_request}\n"

        breaking_change_count = categorised_commit_messages.pop(BREAKING_CHANGE_COUNT_KEY)

        if breaking_change_count > 0:
            release_notes_for_printing += self._create_breaking_change_notification(breaking_change_count)

        release_notes_for_printing += "\n"

        for heading, notes in categorised_commit_messages.items():

            if len(notes) == 0:
                continue

            note_lines = "\n".join(self.list_item_symbol + " " + note for note in notes)
            release_notes_for_printing += f"{heading}\n{note_lines}\n\n"

        release_notes_for_printing += AUTO_GENERATION_END_INDICATOR
        return release_notes_for_printing

    def _create_breaking_change_notification(self, breaking_change_count):
        """Create a notification warning of the number of breaking changes.

        :param str release_notes_for_printing:
        :param dict categorised_commit_messages:
        :return str: release notes with notification added if there are breaking changes
        """
        if breaking_change_count == 1:
            notification = f"There is {breaking_change_count} breaking change."
        else:
            notification = f"There are {breaking_change_count} breaking changes."

        return "**IMPORTANT:** " + notification + "\n"


def main(argv=None):
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "stop_point",
        choices=STOP_POINTS,
        help="The point in the git history to stop compiling commits into the release notes.",
    )

    parser.add_argument(
        "--pull-request-url",
        default=None,
        type=str,
        help="Provide this if you want to update a pull request's description with the generated release notes. Must be provided alongside --api-token if the repository is private.",
    )

    parser.add_argument(
        "--api-token",
        default=None,
        type=str,
        help="A valid GitHub API token for the repository the pull request belongs to. There is no need to provide this if the repository is public.",
    )

    parser.add_argument(
        "--header",
        default="## Contents",
        type=str,
        help="The header (including MarkDown styling) to put the release notes under. Default is '## Contents'",
    )

    parser.add_argument(
        "--list-item-symbol",
        default="-",
        help="The MarkDown list item symbol to use for listing commit messages in the release notes. Default is '- '",
    )

    parser.add_argument(
        "--no-link-to-pull-request",
        action="store_true",
        help="If provided, don't add a link to the given pull request in the release notes.",
    )

    args = parser.parse_args(argv)

    release_notes = ReleaseNotesCompiler(
        stop_point=args.stop_point,
        pull_request_url=args.pull_request_url,
        api_token=args.api_token,
        header=args.header,
        list_item_symbol=args.list_item_symbol,
        include_link_to_pull_request=not args.no_link_to_pull_request,
    ).compile_release_notes()

    print(release_notes)


if __name__ == "__main__":
    main()
