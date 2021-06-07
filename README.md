# pre-commit-hooks
Custom pre-commit hooks used by Octue (see [pre-commit.com](https://pre-commit.com))

## `check-commit-message-is-conventional`
A `commit-msg`-type [`pre-commit`](https://pre-commit.com) hook that checks whether each commit message adheres to the
[Conventional Commits](https://www.conventionalcommits.org/en/v1.0.0/) standard, as well as the additional rules that:
* The header:
  * Uses only the allowed commit codes
  * Is no longer than the maximum header length
  * Ends in a valid pattern
* The body:
  * Is present if required
  * Has lines no longer than the maximum body line length


Use this hook in your repository by adding it to your `.pre-commit-config.yaml` file as:

```yaml
  - repo: https://github.com/octue/pre-commit-hooks
    rev: 0.0.2  # (or another version)
    hooks:
      - id: check-commit-message-is-conventional
        stages: [commit-msg]
        args:
          - --maximum-header-length=72
          - --valid-header-ending-pattern=[A-Za-z\d]
          - --require-body=0
          - --maximum-body-line-length=72
```
