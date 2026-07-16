#!/usr/bin/env python3
"""
Synchronise Essential-Model-Documentation (EMD) entries into the CVs.

For every ``model`` entry in the EMD source branch this opens:

* a pull request into CMIP7-CVs adding the equivalent ``source`` entry, and
* a pull request into WCRP-universe adding the equivalent ``model`` entry.

For every ``horizontal_grid_cell`` entry in the EMD source branch this opens:

* a pull request into CMIP7-CVs adding the equivalent ``grid_label`` entry, and
* a pull request into WCRP-universe adding the equivalent ``grid`` entry.

Grid cells that span more than one region are skipped: they cannot be used for
model output, so they do not belong in the CVs
(https://github.com/WCRP-CMIP/CMIP7-CVs/issues/503).

Existing target entries are left untouched, so re-running the script only ever
adds the entries that are still missing. Pass ``--dry-run`` to print the pull
requests (and the exact file content) that *would* be created without touching
any repository.

Repository and branch identifiers are supplied as command-line options so
nothing is hard-coded. Pull requests into CMIP7-CVs are authorised with
``GITHUB_TOKEN`` and pull requests into WCRP-universe with
``UNIVERSE_ACCESS_TOKEN``, mirroring
``.github/workflows/process-registration-forms.yml``.

This reuses the ``github_form_processor`` package (installed from
``.github/form-processor``), so run it from an environment where that package
and its dependencies (``typer``, ``pydantic``) are installed.
"""

from __future__ import annotations

import base64
import json
import os
from collections.abc import Callable
from dataclasses import dataclass, field
from typing import Any
from urllib.parse import quote, urlencode

import typer
from github_form_processor.github_api import GitHubApiError, GitHubClient
from pydantic import BaseModel, ConfigDict, Field, field_validator

CONTEXT_FILE = "000_context.jsonld"


# --------------------------------------------------------------------------- #
# GitHub client
# --------------------------------------------------------------------------- #


class EmdSyncClient(GitHubClient):
    """``GitHubClient`` extended with the directory/file reads used here."""

    def list_directory(self, path: str, ref: str) -> list[dict[str, Any]]:
        """Return the directory listing for ``path`` on ``ref``."""
        query = urlencode({"ref": ref})
        payload = self._request(
            "GET",
            f"/repos/{self.repository}/contents/{quote(path, safe='/')}?{query}",
        )
        if not isinstance(payload, list):
            raise GitHubApiError(f"Expected `{path}` on `{ref}` to be a directory.")
        return payload

    def get_file_text(self, path: str, ref: str) -> str:
        """Return the decoded UTF-8 content of a file on ``ref``."""
        query = urlencode({"ref": ref})
        payload = self._request(
            "GET",
            f"/repos/{self.repository}/contents/{quote(path, safe='/')}?{query}",
        )
        if isinstance(payload, list):
            raise GitHubApiError(f"Expected `{path}` to be a file, not a directory.")
        return base64.b64decode(payload["content"]).decode("utf-8")

    def existing_filenames(self, directory: str, ref: str) -> set[str]:
        """Return the set of filenames in ``directory`` on ``ref`` (empty if absent)."""
        query = urlencode({"ref": ref})
        payload = self._request(
            "GET",
            f"/repos/{self.repository}/contents/{quote(directory, safe='/')}?{query}",
            allow_404=True,
        )
        if payload is None:
            return set()
        if not isinstance(payload, list):
            raise GitHubApiError(
                f"Expected `{directory}` on `{ref}` to be a directory."
            )
        return {item["name"] for item in payload}

    def open_pull_request_for_branch(self, branch: str) -> dict[str, Any] | None:
        """Return the open pull request whose head is ``branch``, if any."""
        for pull in self.find_pull_requests_for_branch(branch):
            if pull.get("state") == "open":
                return pull
        return None


# --------------------------------------------------------------------------- #
# EMD source models
# --------------------------------------------------------------------------- #


class EmdModel(BaseModel):
    """The subset of an EMD ``model`` entry used to build the CV entries."""

    model_config = ConfigDict(populate_by_name=True, extra="ignore")

    id: str = Field(alias="@id")
    description: str = ""
    validation_key: str = ""

    @property
    def cv_id(self) -> str:
        """The CV identifier: the EMD id with hyphens replaced by underscores."""
        return self.id.replace("-", "_")


class EmdHorizontalGridCell(BaseModel):
    """The subset of an EMD ``horizontal_grid_cell`` entry used here."""

    model_config = ConfigDict(populate_by_name=True, extra="ignore")

    id: str = Field(alias="@id")
    ui_label: str = ""
    region: list[str] = Field(default_factory=list)

    @field_validator("region", mode="before")
    @classmethod
    def _coerce_region(cls, value: Any) -> list[str]:
        if value is None:
            return []
        if isinstance(value, str):
            return [value]
        return list(value)

    @property
    def usable_for_model_output(self) -> bool:
        """Whether this grid can be used for model output, hence belongs in the CVs.

        A grid cell with more than one region cannot be used for model output,
        so it is left out of the CVs rather than treated as an error
        (see https://github.com/WCRP-CMIP/CMIP7-CVs/issues/503).
        """
        return len(self.region) <= 1

    @property
    def region_string(self) -> str:
        """Collapse ``region`` to a single string for the universe CV entry.

        Only meaningful for grids that are usable for model output, i.e. those
        with at most one region.
        """
        if not self.usable_for_model_output:
            raise ValueError(
                f"EMD grid cell {self.id!r} has multiple regions {self.region!r}, "
                "so it is not usable for model output and has no region string "
                "(see https://github.com/WCRP-CMIP/CMIP7-CVs/issues/503)."
            )
        return self.region[0] if self.region else ""


# --------------------------------------------------------------------------- #
# EMD -> CV entry builders
# --------------------------------------------------------------------------- #


def _dumps(entry: dict[str, Any]) -> str:
    """Serialise a CV entry the way the existing entries are stored."""
    return json.dumps(entry, indent=2) + "\n"


def build_source_entry(model: EmdModel) -> tuple[str, str]:
    """Build the CMIP7-CVs ``source`` entry for an EMD model."""
    entry = {"@context": CONTEXT_FILE, "id": model.cv_id, "type": "model"}
    return f"{model.cv_id}.json", _dumps(entry)


def build_universe_model_entry(model: EmdModel) -> tuple[str, str]:
    """Build the WCRP-universe ``model`` entry for an EMD model."""
    entry = {
        "@context": CONTEXT_FILE,
        "id": model.cv_id,
        "type": "model",
        "name": "",
        "family": None,
        "dynamic_components": [],
        "prescribed_components": [],
        "omitted_components": [],
        "description": model.description,
        "calendar": [],
        "release_year": None,
        "references": [],
        "model_components": [],
        "embedded_components": [],
        "coupled_components": [],
        "drs_name": model.validation_key or model.cv_id,
    }
    return f"{model.cv_id}.json", _dumps(entry)


def build_grid_label_entry(grid: EmdHorizontalGridCell) -> tuple[str, str]:
    """Build the CMIP7-CVs ``grid_label`` entry for an EMD grid cell."""
    entry = {"@context": CONTEXT_FILE, "id": grid.id, "type": "grid"}
    return f"{grid.id}.json", _dumps(entry)


def build_universe_grid_entry(grid: EmdHorizontalGridCell) -> tuple[str, str]:
    """Build the WCRP-universe ``grid`` entry for an EMD grid cell."""
    entry = {
        "@context": CONTEXT_FILE,
        "id": grid.id,
        "type": "grid",
        "description": grid.ui_label,
        "drs_name": grid.id,
        "region": grid.region_string,
    }
    return f"{grid.id}.json", _dumps(entry)


# --------------------------------------------------------------------------- #
# Planning and execution
# --------------------------------------------------------------------------- #


@dataclass
class PlannedFile:
    """A single file that would be added to a target directory."""

    path: str
    content: str


@dataclass
class PlannedPullRequest:
    """A pull request the script intends to open in a target repository."""

    client: EmdSyncClient
    repo: str
    base_branch: str
    head_branch: str
    directory: str
    title: str
    body: str
    new_files: list[PlannedFile] = field(default_factory=list)
    existing: list[str] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)


def read_emd_entries(
    client: EmdSyncClient,
    directory: str,
    ref: str,
    model_cls: type[BaseModel],
) -> list[Any]:
    """Read and validate every ``*.json`` entry in an EMD source directory."""
    entries = []
    for item in client.list_directory(directory, ref):
        name = item["name"]
        if item["type"] != "file" or not name.endswith(".json"):
            continue
        raw = client.get_file_text(f"{directory}/{name}", ref)
        entries.append(model_cls.model_validate(json.loads(raw)))
    entries.sort(key=lambda entry: entry.id)
    return entries


@dataclass
class PullRequestTarget:
    """A single directory an EMD entry is synchronised into."""

    client: EmdSyncClient
    repo: str
    base_branch: str
    head_branch: str
    directory: str
    title: str
    body: str
    builder: Callable[[Any], tuple[str, str]]


def plan_pull_requests(
    *,
    targets: list[PullRequestTarget],
    emd_entries: list[Any],
    strict: bool = False,
) -> list[PlannedPullRequest]:
    """Plan a group of coupled pull requests from the same EMD entries.

    The ``targets`` are coupled: every target's entry for a given EMD entry is
    built together, and if building *any* of them fails the entry is skipped for
    *every* target in the group. That keeps the paired repositories (for example
    CMIP7-CVs ``source`` and WCRP-universe ``model``) in step -- a failure on one
    side never leaves a half-synchronised entry on the other.

    If a builder raises for an entry the behaviour depends on ``strict``: when
    ``strict`` is ``True`` the error propagates and planning stops; otherwise the
    error is collected on the first plan's ``errors`` and the entry is skipped
    for the whole group.
    """
    plans = [
        PlannedPullRequest(
            client=target.client,
            repo=target.repo,
            base_branch=target.base_branch,
            head_branch=target.head_branch,
            directory=target.directory,
            title=target.title,
            body=target.body,
        )
        for target in targets
    ]
    present = [
        target.client.existing_filenames(target.directory, target.base_branch)
        for target in targets
    ]
    for emd in emd_entries:
        try:
            built = [target.builder(emd) for target in targets]
        except Exception as error:
            if strict:
                raise
            repos = " and ".join(target.repo for target in targets)
            plans[0].errors.append(
                f"failed to build entry for {getattr(emd, 'id', emd)!r}; "
                f"skipping it for {repos}: {error}"
            )
            continue
        for plan, target_present, (filename, content) in zip(plans, present, built):
            if filename in target_present:
                plan.existing.append(filename)
            else:
                plan.new_files.append(
                    PlannedFile(
                        path=f"{plan.directory}/{filename}", content=content
                    )
                )
    return plans


def describe_plan(plan: PlannedPullRequest, *, show_content: bool) -> None:
    """Print a human-readable description of a planned pull request."""
    typer.echo(f"\n{'=' * 78}")
    typer.echo(f"PR into {plan.repo} ({plan.base_branch} <- {plan.head_branch})")
    typer.echo(f"  title: {plan.title}")
    typer.echo(f"  directory: {plan.directory}/")
    typer.echo(f"  new entries: {len(plan.new_files)}")
    typer.echo(f"  already present (skipped): {len(plan.existing)}")
    if not plan.new_files:
        typer.echo("  -> nothing to add; no pull request needed.")
        return
    for planned in plan.new_files:
        typer.echo(f"    + {planned.path}")
        if show_content:
            for line in planned.content.splitlines():
                typer.echo(f"        {line}")


def apply_plan(plan: PlannedPullRequest) -> None:
    """Create the branch, commit the new files and open the pull request."""
    client = plan.client
    if not plan.new_files:
        typer.echo(f"[{plan.repo}] nothing to add for {plan.directory}/ -- skipping.")
        return

    if not client.branch_exists(plan.head_branch):
        base_sha = client.get_ref_sha(plan.base_branch)
        client.create_branch(plan.head_branch, base_sha)
        typer.echo(f"[{plan.repo}] created branch {plan.head_branch}")
    else:
        typer.echo(f"[{plan.repo}] reusing existing branch {plan.head_branch}")

    for planned in plan.new_files:
        client.put_file(
            planned.path,
            plan.head_branch,
            planned.content,
            f"Add {plan.directory} entry {os.path.basename(planned.path)}",
        )
        typer.echo(f"[{plan.repo}] committed {planned.path}")

    existing_pr = client.open_pull_request_for_branch(plan.head_branch)
    if existing_pr is not None:
        typer.echo(
            f"[{plan.repo}] pull request already open: {existing_pr['html_url']}"
        )
        return

    pull = client.create_pull_request(
        title=plan.title,
        head=plan.head_branch,
        base=plan.base_branch,
        body=plan.body,
    )
    typer.echo(f"[{plan.repo}] opened pull request: {pull['html_url']}")


PR_BODY = (
    "Automated synchronisation of Essential-Model-Documentation entries.\n\n"
    "This pull request adds the `{directory}` entries derived from the EMD "
    "`{emd_directory}` entries on `{emd_repo}@{emd_branch}`.\n\n"
    "Generated by `.github/scripts/sync_emd_entries.py`."
)


def _env_token(*names: str) -> str | None:
    """Return the first non-empty environment variable among ``names``."""
    for name in names:
        value = os.environ.get(name)
        if value:
            return value
    return None


app = typer.Typer(add_completion=False, help=__doc__)


@app.command()
def sync(
    emd_repo: str = typer.Option(
        "WCRP-CMIP/Essential-Model-Documentation", help="EMD source repository."
    ),
    emd_branch: str = typer.Option("src-data", help="EMD source branch."),
    emd_model_dir: str = typer.Option("model", help="EMD model directory."),
    emd_grid_dir: str = typer.Option(
        "horizontal_grid_cell", help="EMD horizontal grid cell directory."
    ),
    cvs_repo: str = typer.Option("WCRP-CMIP/CMIP7-CVs", help="CMIP7-CVs repository."),
    cvs_base_branch: str = typer.Option("esgvoc_dev", help="CMIP7-CVs PR base branch."),
    cvs_source_dir: str = typer.Option("source", help="CMIP7-CVs source directory."),
    cvs_grid_label_dir: str = typer.Option(
        "grid_label", help="CMIP7-CVs grid_label directory."
    ),
    universe_repo: str = typer.Option(
        "WCRP-CMIP/WCRP-universe", help="WCRP-universe repository."
    ),
    universe_base_branch: str = typer.Option(
        "esgvoc_dev", help="WCRP-universe PR base branch."
    ),
    universe_model_dir: str = typer.Option("model", help="WCRP-universe model dir."),
    universe_grid_dir: str = typer.Option("grid", help="WCRP-universe grid dir."),
    branch_prefix: str = typer.Option(
        "emd-sync", help="Prefix for the head branches created for the pull requests."
    ),
    dry_run: bool = typer.Option(
        False, help="Print the pull requests that would be made without creating them."
    ),
    strict: bool = typer.Option(
        False,
        help=(
            "Raise on the first error encountered while building an entry. "
            "Without --strict, such errors are collected and printed instead."
        ),
    ),
) -> None:
    """Open the CMIP7-CVs and WCRP-universe pull requests for the EMD entries."""
    # Pull requests into CMIP7-CVs are authorised with GITHUB_TOKEN and pull
    # requests into WCRP-universe with UNIVERSE_ACCESS_TOKEN, matching how
    # `.github/workflows/process-registration-forms.yml` wires its tokens.
    cvs_token = _env_token("GITHUB_TOKEN", "GH_TOKEN")
    universe_token = _env_token("UNIVERSE_ACCESS_TOKEN") or cvs_token

    emd_client = EmdSyncClient(emd_repo, cvs_token)
    cvs_client = EmdSyncClient(cvs_repo, cvs_token)
    universe_client = EmdSyncClient(universe_repo, universe_token)

    typer.echo(f"Reading EMD entries from {emd_repo}@{emd_branch} ...")
    models = read_emd_entries(emd_client, emd_model_dir, emd_branch, EmdModel)
    grids = read_emd_entries(
        emd_client, emd_grid_dir, emd_branch, EmdHorizontalGridCell
    )
    typer.echo(f"  {len(models)} model entries, {len(grids)} grid entries.")

    # Grid cells spanning more than one region cannot be used for model output,
    # so they do not belong in the CVs at all -- skip them rather than reporting
    # them as errors (https://github.com/WCRP-CMIP/CMIP7-CVs/issues/503).
    unusable_grids = [grid for grid in grids if not grid.usable_for_model_output]
    grids = [grid for grid in grids if grid.usable_for_model_output]
    if unusable_grids:
        typer.echo(
            f"  skipping {len(unusable_grids)} grid entries that span multiple "
            "regions, hence cannot be used for model output:"
        )
        for grid in unusable_grids:
            typer.echo(f"    {grid.id} (regions: {', '.join(grid.region)})")

    def body(directory: str, emd_directory: str) -> str:
        return PR_BODY.format(
            directory=directory,
            emd_directory=emd_directory,
            emd_repo=emd_repo,
            emd_branch=emd_branch,
        )

    # The CMIP7-CVs and WCRP-universe entries derived from the same EMD entries
    # are planned together so a build failure on one side skips the entry on the
    # other side too -- the paired repositories never drift out of sync.
    plans = plan_pull_requests(
        targets=[
            PullRequestTarget(
                client=cvs_client,
                repo=cvs_repo,
                base_branch=cvs_base_branch,
                head_branch=f"{branch_prefix}/source",
                directory=cvs_source_dir,
                title="Add EMD model entries to `source`",
                body=body(cvs_source_dir, emd_model_dir),
                builder=build_source_entry,
            ),
            PullRequestTarget(
                client=universe_client,
                repo=universe_repo,
                base_branch=universe_base_branch,
                head_branch=f"{branch_prefix}/model",
                directory=universe_model_dir,
                title="Add EMD model entries to `model`",
                body=body(universe_model_dir, emd_model_dir),
                builder=build_universe_model_entry,
            ),
        ],
        emd_entries=models,
        strict=strict,
    )
    plans += plan_pull_requests(
        targets=[
            PullRequestTarget(
                client=cvs_client,
                repo=cvs_repo,
                base_branch=cvs_base_branch,
                head_branch=f"{branch_prefix}/grid_label",
                directory=cvs_grid_label_dir,
                title="Add EMD horizontal grid cell entries to `grid_label`",
                body=body(cvs_grid_label_dir, emd_grid_dir),
                builder=build_grid_label_entry,
            ),
            PullRequestTarget(
                client=universe_client,
                repo=universe_repo,
                base_branch=universe_base_branch,
                head_branch=f"{branch_prefix}/grid",
                directory=universe_grid_dir,
                title="Add EMD horizontal grid cell entries to `grid`",
                body=body(universe_grid_dir, emd_grid_dir),
                builder=build_universe_grid_entry,
            ),
        ],
        emd_entries=grids,
        strict=strict,
    )

    # Without --strict, errors raised while building entries are collected on
    # each plan rather than raised; report them before describing the plans.
    errors = [error for plan in plans for error in plan.errors]
    if errors:
        typer.echo(f"\n{len(errors)} error(s) while building entries:")
        for error in errors:
            typer.echo(f"  {error}")

    if dry_run:
        typer.echo(
            "\nDRY RUN -- no branches, commits or pull requests will be created."
        )
        for plan in plans:
            describe_plan(plan, show_content=True)
        total_new = sum(len(plan.new_files) for plan in plans)
        typer.echo(
            f"\n{total_new} entries would be added across {len(plans)} directories."
        )
        return

    for plan in plans:
        describe_plan(plan, show_content=False)
    for plan in plans:
        apply_plan(plan)


if __name__ == "__main__":
    app()
