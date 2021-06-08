# pre-commit-hooks
Custom pre-commit hooks used by Octue (see [pre-commit.com](https://pre-commit.com))

## `check-commit-message-is-conventional`

### Description
A `commit-msg`-type [`pre-commit`](https://pre-commit.com) hook that checks whether each commit message adheres to the
[Conventional Commits](https://www.conventionalcommits.org/en/v1.0.0/) standard, as well as the additional customisable
rules that:
* The header:
  * Uses only the allowed commit codes
  * Is no longer than the maximum header length
  * Ends in a valid pattern
* The body:
  * Is present if required
  * Has lines no longer than the maximum body line length


### Usage
Use this hook in your repository by adding it to your `.pre-commit-config.yaml` file as:

```yaml
  - repo: https://github.com/octue/pre-commit-hooks
    rev: 0.0.2  # (or another version)
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

### Divergence from Conventional Commits specification
Note that while this hook complies with nearly all of the Conventional Commits specification, it is diverges slightly
in the following ways:
* Scopes are disallowed (scopes are an optional part of the specification) for readability and consistency
* `FEA` is used instead of `feat`
* Every extra commit code we have added to the default set consists of three capital letters. This means that
  commit codes (type prefixes) always line up in `git log --oneline` view for ease of viewing and mental (human)
  parsing. We require that they are always provided in uppercase in commit headers, again to increase ease of
  viewing. Despite this, you can add your own codes to this default set that are in whatever form you like (e.g.
  any number of letters in lowercase).
* Footers are not validated against the specification
* Breaking changes are validated but are allowed to appear in the body as well as the footer


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
