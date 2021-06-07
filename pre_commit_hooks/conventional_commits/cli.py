import argparse

from pre_commit_hooks.conventional_commits.checker import ConventionalCommitMessageChecker


RED = "\033[0;31m"
NO_COLOUR = "\033[0m"


def main(argv=None):
    """Check if the git commit message adheres to the Conventional Commits standard and additional rules.

    :param iter(str)|None argv: iterable containing single argument, which should be the path to a git commit message
    :return int: the return code - 0 if the message passes, 1 if it fails
    """
    parser = argparse.ArgumentParser()
    parser.add_argument("commit_message_path", type=str, help="Path to current git commit message.")

    args = parser.parse_args(argv)

    with open(args.commit_message_path) as f:
        commit_message_lines = f.read().splitlines()

    try:
        ConventionalCommitMessageChecker().check_commit_message(commit_message_lines)
    except ValueError as e:
        print(f"{RED}COMMIT MESSAGE FAILED CHECKS:{NO_COLOUR} {e}")
        return 1

    return 0


if __name__ == "__main__":
    exit(main())
