import re
import argparse
import os
import subprocess


ALLOWED_COMMIT_CODES = {"FEA", "IMP", "FIX", "OPS", "DEP", "REF", "TST", "CLN", "OPT", "MRG", "REV", "CHO"}
CODE_SEPARATOR = ": "
MAXIMUM_HEADER_LENGTH = 72
VALID_HEADER_ENDINGS = re.compile(r"[A-Za-z\d]")
MAXIMUM_BODY_LINE_LENGTH = 72


def check_commit_message(commit_message_lines, require_body=False):
    if len(commit_message_lines) == 0:
        raise ValueError("Commit message should not be empty.")

    header = commit_message_lines[0]
    _check_header(header)

    try:
        header_separator = commit_message_lines[1]
        body = commit_message_lines[2:]
    except IndexError:
        if require_body:
            raise ValueError(
                f"A body (separated from the header by a blank newline) is required in the commit message; received "
                f"{commit_message_lines!r}."
            )
        return

    if len(header_separator) > 0:
        raise ValueError("There should be blank line between the header and the body.")

    _check_body(body, require_body=require_body)


def _check_header(header):
    if len(header) == 0:
        raise ValueError("The commit header should not be blank.")

    if not any(header.startswith(code + CODE_SEPARATOR) for code in ALLOWED_COMMIT_CODES):
        raise ValueError(
            f"Commit headers should start with one of the allowed commit codes {ALLOWED_COMMIT_CODES!r}; received "
            f"{header!r}."
        )

    if len(header) > MAXIMUM_HEADER_LENGTH:
        raise ValueError(
            f"The commit header should be no longer than {MAXIMUM_HEADER_LENGTH} characters; it is currently "
            f"{len(header)} characters."
        )

    if not re.match(VALID_HEADER_ENDINGS, header[-1]):
        raise ValueError(f"The commit header can only end in a letter or number; received {header!r}.")


def _check_body(body, require_body=False):
    if require_body and len(body) == 1 and len(body[0]) == 0:
        raise ValueError("A commit body is required but is blank.")

    for line in body:
        if len(line) > MAXIMUM_BODY_LINE_LENGTH:
            raise ValueError(
                f"The maximum line length of the body is {MAXIMUM_BODY_LINE_LENGTH} characters; the line {line!r} is "
                f"{len(line)} characters."
            )
