import argparse
import os
import subprocess
import sys


RED = "\033[0;31m"
GREEN = "\033[0;32m"
NO_COLOUR = "\033[0m"


VERSION_PARAMETERS = {
    "setup.py": [["python", "setup.py", "--version"], False],
    "poetry": [["poetry", "version", "-s"], False],
    "npm": ["""npm version --json | jq --raw-output '.["{}"]'""", True],
}


def get_current_version(version_source, package_name=None, version_source_file=None):
    """Get the current version of the package via the given version source. If getting the version via `npm` from a
    `package.json` file, the name of the package is required.

    :param str version_source: the name of the method to use to acquire the current version number (one of "setup.py", "poetry", or "npm")
    :param str|None package_name: the name of the package if it is needed for getting the version (e.g. for npm)
    :param str|None version_source_file: the path to the version source file if it is not in the current working directory
    :return str:
    """
    original_directory = os.path.abspath(os.getcwd())
    version_parameters = VERSION_PARAMETERS[version_source]

    if package_name:
        version_parameters[0] = version_parameters[0].format(package_name)

    if version_source_file:
        file_directory = os.path.abspath(os.path.dirname(version_source_file))
        os.chdir(file_directory)

    try:
        process = subprocess.run(version_parameters[0], shell=version_parameters[1], capture_output=True)
    finally:
        if version_source_file:
            os.chdir(original_directory)

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
    parser = argparse.ArgumentParser()
    parser.add_argument("version_source")
    parser.add_argument("--package-name", default=None)
    parser.add_argument("--file", default=None)

    args = parser.parse_args(argv)

    current_version = get_current_version(
        version_source=args.version_source, package_name=args.package_name, version_source_file=args.file
    )

    expected_semantic_version = get_expected_semantic_version()

    if current_version == "null":
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
