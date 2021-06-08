import argparse
import os
import subprocess

from pre_commit_hooks.conventional_commits.checker import ConventionalCommitMessageChecker


RED = "\033[0;31m"
NO_COLOUR = "\033[0m"


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
    parser.add_argument("--maximum-header-length", default=72, type=int)
    parser.add_argument("--valid-header-ending-pattern", default=r"[A-Za-z\d]", type=str)
    parser.add_argument("--require-body", default=False, type=bool)
    parser.add_argument("--maximum-body-line-length", default=72, type=int)

    args = parser.parse_args(argv)

    try:
        ConventionalCommitMessageChecker(
            maximum_header_length=args.maximum_header_length,
            valid_header_ending_pattern=args.valid_header_ending_pattern,
            require_body=args.require_body,
            maximum_body_line_length=args.maximum_body_line_length,
        ).check_commit_message(commit_message_lines)
    except ValueError as e:
        print(f"{RED}COMMIT MESSAGE FAILED CHECKS:{NO_COLOUR} {e}")
        return 1

    return 0
