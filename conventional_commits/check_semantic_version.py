import subprocess
import sys


RED = "\033[0;31m"
GREEN = "\033[0;32m"
NO_COLOUR = "\033[0m"


VERSION_PARAMETERS = {
    "setup.py": (["python", "setup.py", "--version"], False),
    "poetry": (["poetry", "version", "-s"], False),
    "npm": ("""npm version --json | jq --raw-output '.["planex-site"]'""", True),
}


def get_current_version(version_source):
    """Get the current version of the package via the given version source.

    :param str version_source: the name of the method to use to acquire the current version number (one of "setup.py", "poetry", or "npm")
    :return str:
    """
    version_parameters = VERSION_PARAMETERS[version_source]
    process = subprocess.run(version_parameters[0], shell=version_parameters[1], capture_output=True)
    return process.stdout.strip().decode("utf8")


def get_expected_semantic_version():
    """Get the expected semantic version for the package as of the current HEAD git commit.

    :return str:
    """
    process = subprocess.run(["git-mkver", "next"], capture_output=True)
    return process.stdout.strip().decode("utf8")


def main():
    """Compare the current version to the expected semantic version. If they match, exit successfully with an exit code
    of 0; if they don't, exit with an exit code of 1.

    :return None:
    """
    current_version = get_current_version(version_source=sys.argv[1])
    expected_semantic_version = get_expected_semantic_version()

    if current_version != expected_semantic_version:
        print(
            f"{RED}VERSION FAILED CHECKS:{NO_COLOUR} The current version ({current_version}) is different from the "
            f"expected semantic version ({expected_semantic_version})."
        )
        sys.exit(1)

    print(
        f"{GREEN}VERSION PASSED CHECKS:{NO_COLOUR} The current version is the same as the expected semantic version: "
        f"{expected_semantic_version}."
    )
    sys.exit(0)


if __name__ == "__main__":
    main()
