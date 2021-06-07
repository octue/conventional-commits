import argparse

from conventional_commits.checker import ConventionalCommitMessageChecker


def main(argv=None):
    """

    :param iter(str)|None argv:
    :return int:
    """
    parser = argparse.ArgumentParser()
    parser.add_argument('commit_message_path', type=str, help='Path to current git commit message.')

    args = parser.parse_args(argv)

    with open(args[0]) as f:
        commit_message_lines = f.readlines()

    try:
        ConventionalCommitMessageChecker().check_commit_message(commit_message_lines)
    except ValueError:
        return 1

    return 0


if __name__ == '__main__':
    exit(main())
