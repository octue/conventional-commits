import argparse
import os
import re
import subprocess


ALLOWED_COMMIT_CODES = {
    "FEA": "A new feature",
    "ENH": "An improvement or optimisation to an existing feature",
    "FIX": "A bug fix",
    "OPS": "An operational/devops/git change e.g. to continuous integration scripts or GitHub templates",
    "DEP": "A change in dependencies",
    "REF": "A refactor of existing code",
    "TST": "A change to tests or the testing framework",
    "MRG": "A merge commit",
    "REV": "A reversion e.g. a `git revert` commit",
    "CHO": "A chore e.g. updating a menial configuration file or .gitignore file",
    "WIP": "A work-in-progress commit (usually to be avoided, but makes sense for e.g. trying changes in git-based CI)",
    "DOC": "A change to documentation, docstrings, or documentation generation",
    "STY": "A change to code style specifications or to code to conform to new style",
}

CODE_SEPARATOR = ": "

BREAKING_CHANGE_INDICATORS = {"BREAKING-CHANGE", "BREAKING CHANGE"}
BREAKING_CHANGE_PATTERN = rf"({'|'.join(BREAKING_CHANGE_INDICATORS)}): ([A-Za-z\d]+)"

RED = "\033[0;31m"
NO_COLOUR = "\033[0m"


class ConventionalCommitMessageChecker:
    """A class that checks whether the given commit message adheres to Conventional Commits standard, as well as the
    additional rules that:
    * The header:
      * Uses only allowed commit codes
      * Is no longer than the maximum header length
      * Ends in a valid pattern
    * The body:
      * Is present if required
      * Has lines no longer than the maximum body line length

    Note that this checker is slightly divergent from the Conventional Commits specification in the following ways:
    * Scopes are disallowed (scopes are an optional part of the specification) for readability and consistency
    * "FEA" is used instead of "feat"
    * Every extra commit code we have added to the default set consists of three capital letters. This means that
      commit codes (type prefixes) always line up in `git log --oneline` view for ease of viewing and mental (human)
      parsing. We require that they are always provided in uppercase in commit headers, again to increase ease of
      viewing. Despite this, you can add your own codes to this default set that are in whatever form you like (e.g.
      any number of letters in lowercase).
    * Footers are not validated against the specification
    * Breaking changes are validated but are allowed to appear in the body as well as the footer

    See https://www.conventionalcommits.org for more information.

    :param iter(str)|None allowed_commit_codes: allowed codes for the very beginning of the header
    :param int maximum_header_length: maximum number of characters allowed in the header
    :param str valid_header_ending_pattern: regex pattern of allowed endings for the header
    :param bool require_body: if True, a body is required in the commit message
    :param int maximum_body_line_length: maximum length of each line in the body
    :return None:
    """

    def __init__(
        self,
        allowed_commit_codes=None,
        maximum_header_length=72,
        valid_header_ending_pattern=r"[A-Za-z\d]",
        require_body=False,
        maximum_body_line_length=72,
    ):
        self.allowed_commit_codes = allowed_commit_codes or ALLOWED_COMMIT_CODES
        self.maximum_header_length = maximum_header_length
        self.valid_header_ending_pattern = valid_header_ending_pattern
        self.require_body = require_body
        self.maximum_body_line_length = maximum_body_line_length

    def check_commit_message(self, commit_message_lines):
        """Check that the given commit message conforms to the Conventional Commit standard and given rules.

        :param iter(str) commit_message_lines:
        :raise ValueError: if the commit fails any of the checks
        :return None:
        """
        self._remove_comment_lines(commit_message_lines)

        if len(commit_message_lines) == 0:
            raise ValueError("The commit message should not be empty.")

        header = commit_message_lines[0]
        self._check_header(header)

        # Check if a body is present.
        try:
            header_separator = commit_message_lines[1]
            body = commit_message_lines[2:]

        # If it isn't, raise an error if it was required.
        except IndexError:
            if self.require_body:
                raise ValueError(
                    f"A body (separated from the header by a blank line) is required in the commit message; received "
                    f"{commit_message_lines[0]!r}."
                )
            return

        if len(header_separator) > 0:
            raise ValueError("There should be blank line between the header and the body.")

        self._check_body(body)

    def _remove_comment_lines(self, commit_message_lines):
        """Remove comment lines so they are ignored by the other steps of the checker.

        :param iter(str) commit_message_lines:
        :return iter(str):
        """
        comment_line_indexes = [i for i, line in enumerate(commit_message_lines) if line.startswith("#")]

        number_of_comment_lines_deleted = 0
        for index in comment_line_indexes:
            commit_message_lines.pop(index - number_of_comment_lines_deleted)
            number_of_comment_lines_deleted += 1

    def _check_header(self, header):
        """Check that the header conforms to the given rules.

        :param str header:
        :raise ValueError: if the header fails any of the checks
        :return None:
        """
        if len(header) == 0:
            raise ValueError("The commit header should not be blank.")

        if not any(header.startswith(code + CODE_SEPARATOR) for code in self.allowed_commit_codes.keys()):
            pretty_formatted_allowed_commit_codes = "\n".join(
                f" - {key!r}: {value}" for key, value in self.allowed_commit_codes.items()
            )

            raise ValueError(
                f"Commit headers should start with one of the allowed commit codes:"
                f"\n{pretty_formatted_allowed_commit_codes}\nand be separated from the header message by "
                f"{CODE_SEPARATOR!r}. Received {header!r}."
            )

        if len(header) > self.maximum_header_length:
            raise ValueError(
                f"The commit header should be no longer than {self.maximum_header_length} characters; received "
                f"{header!r}, which is {len(header)} characters long."
            )

        if not re.compile(self.valid_header_ending_pattern).match(header[-1]):
            raise ValueError(
                f"The commit header must end in a character matching the pattern {self.valid_header_ending_pattern!r}; "
                f"received {header!r}."
            )

    def _check_body(self, body):
        """Check that the body conforms to the given rules.

        :param iter(str) body:
        :raise ValueError: if the body fails any of the checks
        :return None:
        """
        if self.require_body and len(body) == 1 and len(body[0]) == 0:
            raise ValueError("The commit body should not be blank.")

        for line in body:
            if len(line) > self.maximum_body_line_length:
                raise ValueError(
                    f"The maximum line length of the body is {self.maximum_body_line_length} characters; the line "
                    f"{line!r} is {len(line)} characters."
                )

            self._validate_breaking_change_descriptions(line)

    def _validate_breaking_change_descriptions(self, line):
        """Check that any breaking change indicators (one of "BREAKING CHANGE" or "BREAKING-CHANGE") are in uppercase
        and followed by a colon and space (": ") preceding a description.

        :param str line:
        :raise ValueError: if the breaking change indicator is invalid
        :return None:
        """
        breaking_change_error = ValueError(
            f"Breaking changes must be denoted by one of {BREAKING_CHANGE_INDICATORS!r} in uppercase followed by ': ' "
            f"and a description e.g. 'BREAKING CHANGE: Change MyPublicClass interface'; received "
            f"{line!r}."
        )

        if any(indicator.lower() in line for indicator in BREAKING_CHANGE_INDICATORS):
            raise breaking_change_error

        if any(indicator in line for indicator in BREAKING_CHANGE_INDICATORS):
            if not re.match(BREAKING_CHANGE_PATTERN, line):
                raise breaking_change_error


def main(argv=None):
    """Check if the git commit message adheres to the Conventional Commits standard and additional rules.

    :param iter(str)|None argv: iterable containing single argument, which should be the path to a git commit message
    :return int: the return code - 0 if the message passes, 1 if it fails
    """
    repository_path = (
        subprocess.run(["git", "rev-parse", "--show-toplevel"], capture_output=True).stdout.decode().strip()
    )

    with open(os.path.join(repository_path, ".git", "COMMIT_EDITMSG")) as f:
        commit_message_lines = f.read().splitlines()

    parser = argparse.ArgumentParser()
    parser.add_argument("--allowed-commit-codes", default=None)
    parser.add_argument("--additional-commit-codes", default=None)
    parser.add_argument("--maximum-header-length", default=72, type=int)
    parser.add_argument("--valid-header-ending-pattern", default=r"[A-Za-z\d]", type=str)
    parser.add_argument("--require-body", default=False, type=bool)
    parser.add_argument("--maximum-body-line-length", default=72, type=int)

    args = parser.parse_args(argv)

    try:
        if args.allowed_commit_codes:
            allowed_commit_codes = {code: None for code in args.allowed_commit_codes.split(",")}
        elif args.additional_commit_codes:
            allowed_commit_codes = {
                **ALLOWED_COMMIT_CODES,
                **{code: None for code in args.additional_commit_codes.split(",")},
            }
        else:
            allowed_commit_codes = None

        ConventionalCommitMessageChecker(
            allowed_commit_codes=allowed_commit_codes,
            maximum_header_length=args.maximum_header_length,
            valid_header_ending_pattern=args.valid_header_ending_pattern,
            require_body=args.require_body,
            maximum_body_line_length=args.maximum_body_line_length,
        ).check_commit_message(commit_message_lines)
    except ValueError as e:
        print(f"{RED}COMMIT MESSAGE FAILED CHECKS:{NO_COLOUR} {e}")
        return 1

    return 0
