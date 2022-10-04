[![Release](https://github.com/octue/conventional-commits/actions/workflows/release.yml/badge.svg)](https://github.com/octue/conventional-commits/actions/workflows/release.yml)
[![codecov](https://codecov.io/gh/octue/conventional-commits/branch/main/graph/badge.svg?token=IE19ANFKET)](https://codecov.io/gh/octue/conventional-commits)
[![pre-commit](https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit&logoColor=white)](https://github.com/pre-commit/pre-commit)
[![black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/ambv/black)

# Continuous deployment via Conventional Commits

This package enables continuous deployment using [Conventional Commits](https://www.conventionalcommits.org/en/v1.0.0/)
via two GitHub actions and a `pre-commit` hook:
- A [semantic version](https://semver.org/) checker that uses [`git-mkver`](https://github.com/idc101/git-mkver) to
predict what the version of the package should be as of the `HEAD` commit and checks if this matches the version as
currently stated in a `setup.py`, `setup.cfg`, `pyproject.toml`, or `package.json` file.
- A pull request description generator that categorises all the commit messages in a pull request and compiles them into
  a well-formatted description ready to be used as release notes. These can be used to automatically update a section of
  the pull request description on every push while leaving the rest of the description as-is.
- A `commit-msg`-type [`pre-commit`](https://pre-commit.com) hook that checks if the current commit message adheres to
the Conventional Commit standard.

The GitHub actions can be combined with an automatic release-on-pull-request-merge workflow to facilitate continuous
deployment of correctly semantically-versioned code changes to your users (as long as all contributers categorise their
commits correctly as breaking changes, new features, and bug-fixes/small-changes). Examples of workflows that do this
are linked below. You can find an example release workflow [here](.github/workflows/release.yml).

## Contents
* [Commit message pre-commit hook](#conventional-commit-message-pre-commit-hook)
* [Semantic version checker](https://github.com/octue/check-semantic-version) - **this has now been moved to its own
  repository**
* [Pull request description generator](https://github.com/octue/generate-pull-request-description) - **this has now been
  moved to its own repository**

## Conventional commit message pre-commit hook

### Description

A `commit-msg`-type [`pre-commit`](https://pre-commit.com) hook that checks whether each commit message adheres to the
[Conventional Commits](https://www.conventionalcommits.org/en/v1.0.0/) standard, as well as the additional customisable
rules that:

- The header:
  - Uses only the allowed commit codes
  - Is no longer than the maximum header length
  - Ends in a valid pattern
- The body:
  - Is present if required
  - Has lines no longer than the maximum body line length

You can provide values for each of these rules, including another set of commit codes to override or augment the
defaults.

### Default allowed commit codes

You can change these for a repository (see 'Usage' below) for your requirements. Across octue, we use:

- `FEA`: A new feature
- `ENH`: An improvement or optimisation to an existing feature
- `FIX`: A bug fix
- `OPS`: An operational/devops/git change e.g. to continuous integration scripts or GitHub templates
- `DEP`: A change in dependencies
- `REF`: A refactor of existing code
- `TST`: A change to tests or the testing framework
- `MRG`: A merge commit
- `REV`: A reversion e.g. a `git revert` commit
- `CHO`: A chore e.g. updating a menial configuration file or .gitignore file
- `WIP`: A work-in-progress commit (usually to be avoided, but makes sense for e.g. trying changes in git-based CI)
- `DOC`: A change to documentation, docstrings, or documentation generation
- `STY`: A change to code style specifications or to code to conform to new style

### Usage

Use this hook in your repository by adding it to your `.pre-commit-config.yaml` file as:

```yaml
- repo: https://github.com/octue/conventional-commits
  rev: 0.0.2 # (or another version)
  hooks:
    - id: check-commit-message-is-conventional
      stages: [commit-msg]
      args:
        - --additional-commit-codes=ABC,DEF,GHI
        - --maximum-header-length=72
        - --valid-header-ending-pattern=[A-Za-z\d]
        - --require-body=0
        - --maximum-body-line-length=72
```

Then, install `pre-commit` if you haven't already:

```shell
pip install pre-commit
```

Finally, install the hook:

```shell
pre-commit install && pre-commit install -t commit-msg
```

### Divergence from Conventional Commits specification

Note that while this hook complies with nearly all of the Conventional Commits specification, it is diverges slightly
in the following ways:

- Scopes are disallowed (scopes are an optional part of the specification) for readability and consistency
- `FEA` is used instead of `feat`
- Every extra commit code we have added to the default set consists of three capital letters. This means that
  commit codes (type prefixes) always line up in `git log --oneline` view for ease of viewing and mental (human)
  parsing. We require that they are always provided in uppercase in commit headers, again to increase ease of
  viewing. Despite this, you can add your own codes to this default set that are in whatever form you like (e.g.
  any number of letters in lowercase).
- Footers are not validated against the specification
- Breaking changes are validated but are allowed to appear in the body as well as the footer

### Readability gains of 3-letter uppercase commit codes/types

Only using 3-letter uppercase commit codes/types results in a uniform, easily readable git log. There is a clear
distinction between the code and the title of the commit, and the eye doesn't have to jump left and right on each new
line to find the start of the title. Here is an example from our own git log:

```git
>>> git log --oneline -10

82f5953 ENH: Validate breaking change indicators in commit messages  (HEAD -> main)
810944a ENH: Improve range of commit codes available
311f4f5 REF: Move comment removal into method  (origin/main, origin/HEAD)
ba2aca3 IMP: Explain commit codes in error message
f0142c2 DOC: Update README
214af4f TST: Test optional CLI args
417efcc IMP: Add DOC and LOG commit codes
d528edd OPS: Use version of hook specified in this repo locally
5b5727c IMP: Allow options to be passed to hook
86e07c5 CLN: Apply pre-commit checks to all files
```
