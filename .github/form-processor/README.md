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
  --cmip7-repository "${GITHUB_REPOSITORY}" \
  --pr-base-branch esgvoc_dev \
  --universe-repository WCRP-CMIP/WCRP-universe \
  --universe-base-branch main \
  --experiment-output-dir experiment \
  --activity-output-dir activity \
  --institution-output-dir institution \
  --universe-organisation-dir organisation \
  --universe-institution-dir institution \
  --wcrp-universe-url https://raw.githubusercontent.com/WCRP-CMIP/WCRP-universe/main \
  --cmip7-cvs-path "${GITHUB_WORKSPACE}"
```

against the issue event payload supplied by GitHub.

The repositories and base branches are passed in from the workflow so that no
repository identity is hard-coded in this package. `GITHUB_TOKEN` authorises
pull requests into the CMIP7-CVs repository, while `UNIVERSE_ACCESS_TOKEN`
authorises pull requests into the WCRP universe repository.

To check CMIP7 CV entries from a remote URL instead of a local checkout, use
`--cmip7-cvs-url https://example.test/CMIP7-CVs`. That option is ignored when
`--cmip7-cvs-path` is set.

## Registration targets

Each registration is routed to the appropriate repository:

| Registration         | Repository      | Directory      | Notes                                   |
| -------------------- | --------------- | -------------- | --------------------------------------- |
| experiment           | CMIP7-CVs       | `experiment`   |                                         |
| activity             | CMIP7-CVs       | `activity`     |                                         |
| institution          | WCRP universe   | `organisation` | full organisation entry                 |
|                      | CMIP7-CVs       | `institution`  | stub pointing at the universe entry     |
| institution-member   | WCRP universe   | `institution`  |                                         |

An institution therefore opens two pull requests (one per repository); the
others open a single pull request.

## Generated Pull Requests

The workflow uses deterministic branches of the form

```text
registration/{experiment|activity|institution|institution-member}-{issue-number}-{id}
```

New issue submissions create a pull request per target repository. CMIP7-CVs
pull requests target the `esgvoc_dev` branch and WCRP universe pull requests
target `main`. Edits update the existing branches and pull requests.
If an edited issue has no open registration pull request,
the processor opens a new one.

## Testing the workflow

`test-registration-forms.yml` reconstructs the event payload for a single,
hard-coded issue (`DEFAULT_ISSUE_NUMBER`, overridable via a `workflow_dispatch`
input) so the processor can be exercised on a branch before merging, or run on
demand rather than waiting for a real issue event.
