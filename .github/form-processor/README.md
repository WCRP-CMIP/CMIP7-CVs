# GitHub Form Processor

This package processes repository issue forms into validated registration JSON
files and opens pull requests with the generated files.

## Installation

To create the local development environment, run

```sh
uv sync
```

Run the tests with

```sh
uv run pytest
```

The GitHub Actions workflow installs this package and runs

```sh
python -m github_form_processor \
  --experiment-output-dir experiment \
  --activity-output-dir activity \
  --wcrp-universe-url https://raw.githubusercontent.com/WCRP-CMIP/WCRP-universe/esgvoc \
  --cmip7-cvs-url https://raw.githubusercontent.com/WCRP-CMIP/CMIP7-CVs/esgvoc
```

against the issue event payload supplied by GitHub.

To check CMIP7 CV entries from a local checkout instead of a remote URL, use
`--cmip7-cvs-path /path/to/CMIP7-CVs`. In that mode, `--cmip7-cvs-url` is not
used.

## Generated Pull Requests

The workflow uses deterministic branches of the form

```text
registration/{experiment|activity}-{issue-number}-{id}
```

New issue submissions create a pull request. Edits update the existing pull
request branch. If an edited issue has no open registration pull request, the
processor comments on the issue and exits with an error.
