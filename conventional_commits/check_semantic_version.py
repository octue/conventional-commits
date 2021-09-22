import argparse
import copy
import os
import subprocess
import sys


RED = "\033[0;31m"
GREEN = "\033[0;32m"
NO_COLOUR = "\033[0m"


VERSION_PARAMETERS = {
    "setup.py": [["python", "setup.py", "--version"], False],
    "pyproject.toml": [["poetry", "version", "-s"], False],
    "package.json": ["""cat {} | jq --raw-output '.["version"]'""", True],
}


def get_current_version(version_source, version_source_file=None):
    """Get the current version of the package via the given version source. The relevant file containing the version
    information is assumed to be in the current working directory unless `version_source_file` is given.

    :param str version_source: the name of the method to use to acquire the current version number (one of "setup.py", "pyproject.toml", or "package.json")
    :param str|None version_source_file: the path to the version source file if it is not in the current working directory
    :return str:
    """
    try:
        version_parameters = copy.deepcopy(VERSION_PARAMETERS[version_source])
    except KeyError:
        raise ValueError(
            f"Unsupported version source received: {version_source!r}; options are {list(VERSION_PARAMETERS.keys())!r}."
        )

    original_working_directory = os.getcwd()

    if version_source in {"setup.py", "pyproject.toml"}:
        if version_source_file:
            os.chdir(os.path.dirname(version_source_file))

    elif version_source == "package.json":
        if version_source_file:
            version_parameters[0] = version_parameters[0].format(version_source_file)
        else:
            version_parameters[0] = version_parameters[0].format("package.json")

    process = subprocess.run(version_parameters[0], shell=version_parameters[1], capture_output=True)

    if os.getcwd() != original_working_directory:
        os.chdir(original_working_directory)

    return process.stdout.strip().decode("utf8")


def get_expected_semantic_version():
    """Get the expected semantic version for the package as of the current HEAD git commit.

    :return str:
    """
    process = subprocess.run(["git-mkver", "next"], capture_output=True)
    return process.stdout.strip().decode("utf8")


def main(argv=None):
    """Compare the current version to the expected semantic version. If they match, exit successfully with an exit code
    of 0; if they don't, exit with an exit code of 1.

    :return None:
    """
    if not os.path.exists("mkver.conf"):
        raise FileNotFoundError(
            "A mkver.conf file is required in the current working directory (usually the repository root) in order to "
            "check the semantic version."
        )

    parser = argparse.ArgumentParser()
    parser.add_argument("version_source")
    parser.add_argument("--file", default=None)

    args = parser.parse_args(argv)

    current_version = get_current_version(version_source=args.version_source, version_source_file=args.file)
    expected_semantic_version = get_expected_semantic_version()

    if not current_version or current_version == "null":
        print(f"{RED}VERSION FAILED CHECKS:{NO_COLOUR} No current version found.")
        sys.exit(1)

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
