"""Command-line interface for processing registration issue forms."""

from __future__ import annotations

import json
import os
from dataclasses import dataclass
from pathlib import Path
from urllib.parse import urlsplit

import typer

from github_form_processor.cv import CvClient
from github_form_processor.format import (
    format_edit_error_comment,
    format_output_path_for_identifier,
    format_success_comment,
    format_validation_comment,
)
from github_form_processor.github_api import GitHubApiError, GitHubClient
from github_form_processor.processor import (
    PreparedRegistration,
    RegistrationOutput,
    prepare_registration,
)

app = typer.Typer(no_args_is_help=True)

ASSIGNEES = ["znichollscr", "ltroussellier"]


def repository_slug(value: str) -> str:
    """Normalise a repository reference to an `owner/name` slug.

    Accepts either an `owner/name` slug or a full URL such as
    `https://github.com/owner/name` (optionally with a trailing slash or a
    `.git` suffix).
    """
    text = value.strip().rstrip("/").removesuffix(".git")
    if "://" in text:
        text = urlsplit(text).path
    segments = [segment for segment in text.split("/") if segment]
    if len(segments) < 2:
        raise ValueError(f"Could not parse a repository slug from {value!r}.")
    return f"{segments[-2]}/{segments[-1]}"


@dataclass(frozen=True)
class RepoTarget:
    """A resolved repository to open a registration pull request in."""

    client: GitHubClient
    base_branch: str


@app.command("process")
def process_issue_form(
    event_path: Path | None = typer.Option(
        None,
        "--event-path",
        help="Path to the GitHub event JSON payload. Defaults to GITHUB_EVENT_PATH.",
    ),
    cmip7_repository: str | None = typer.Option(
        None,
        "--cmip7-repository",
        help=(
            "URL or owner/name slug of the CMIP7-CVs repository. "
            "Defaults to GITHUB_REPOSITORY."
        ),
    ),
    pr_base_branch: str = typer.Option(
        "esgvoc_dev",
        "--pr-base-branch",
        help="Base branch for pull requests opened in the CMIP7-CVs repository.",
    ),
    universe_repository: str = typer.Option(
        "https://github.com/WCRP-CMIP/WCRP-universe",
        "--universe-repository",
        help="URL or owner/name slug of the WCRP universe repository.",
    ),
    universe_base_branch: str = typer.Option(
        "esgvoc_dev",
        "--universe-base-branch",
        help=(
            "Base branch for pull requests opened in the WCRP universe repository. "
            "The WCRP universe CV lookup URL is derived from --universe-repository "
            "and this branch."
        ),
    ),
    experiment_output_dir: str = typer.Option(
        "experiment",
        "--experiment-output-dir",
        help="Directory for generated experiment JSON files (CMIP7-CVs).",
    ),
    activity_output_dir: str = typer.Option(
        "activity",
        "--activity-output-dir",
        help="Directory for generated activity JSON files (CMIP7-CVs).",
    ),
    institution_output_dir: str = typer.Option(
        "institution",
        "--institution-output-dir",
        help="Directory for the generated institution stub JSON files (CMIP7-CVs).",
    ),
    universe_organisation_dir: str = typer.Option(
        "organisation",
        "--universe-organisation-dir",
        help="Directory for generated organisation JSON files (WCRP universe).",
    ),
    universe_institution_dir: str = typer.Option(
        "institution",
        "--universe-institution-dir",
        help="Directory for generated institution JSON files (WCRP universe).",
    ),
    skip_external_checks: bool = typer.Option(
        False,
        "--skip-external-checks",
        help="Skip CV and URL checks.",
    ),
    cmip7_cvs_url: str = typer.Option(
        "https://raw.githubusercontent.com/WCRP-CMIP/CMIP7-CVs/esgvoc",
        "--cmip7-cvs-url",
        help="URL root for CMIP7 CV JSON files. Ignored when --cmip7-cvs-path is set.",
    ),
    cmip7_cvs_path: Path | None = typer.Option(
        None,
        "--cmip7-cvs-path",
        exists=True,
        file_okay=False,
        dir_okay=True,
        readable=True,
        resolve_path=True,
        help="Local CMIP7-CVs repository checkout to use instead of --cmip7-cvs-url.",
    ),
) -> None:
    """Process one GitHub issue event into registration pull requests."""
    event_path = event_path or _event_path_from_environment()
    event = json.loads(event_path.read_text())
    issue = event.get("issue")
    if not issue:
        typer.echo("Event does not contain an issue payload.")
        raise typer.Exit(0)

    cmip7_repository = cmip7_repository or os.environ.get("GITHUB_REPOSITORY")
    if not cmip7_repository:
        typer.echo(
            "A CMIP7-CVs repository must be set via --cmip7-repository or "
            "GITHUB_REPOSITORY.",
            err=True,
        )
        raise typer.Exit(2)

    try:
        cmip7_repository = repository_slug(cmip7_repository)
        universe_repository = repository_slug(universe_repository)
    except ValueError as exc:
        typer.echo(str(exc), err=True)
        raise typer.Exit(2) from exc

    # The WCRP universe CV lookup URL is derived from the universe repository and
    # its base branch, so the repository is configured in a single place.
    wcrp_universe_url = (
        f"https://raw.githubusercontent.com/{universe_repository}/"
        f"{universe_base_branch}"
    )

    preparation = prepare_registration(
        issue=issue,
        cmip7_repository=cmip7_repository,
        universe_repository=universe_repository,
        experiment_output_dir=experiment_output_dir,
        activity_output_dir=activity_output_dir,
        institution_output_dir=institution_output_dir,
        universe_organisation_dir=universe_organisation_dir,
        universe_institution_dir=universe_institution_dir,
        external_checks=not skip_external_checks,
        cv_client=CvClient(
            wcrp_universe_url=wcrp_universe_url,
            cmip7_cvs_url=cmip7_cvs_url,
            cmip7_cvs_path=cmip7_cvs_path,
        ),
    )
    if preparation.prepared is None and not preparation.validation_errors:
        typer.echo("Issue does not match a known registration form.")
        raise typer.Exit(0)

    token = os.environ.get("GITHUB_TOKEN")
    if not token:
        typer.echo(
            "The GITHUB_TOKEN environment variable must be set.",
            err=True,
        )
        raise typer.Exit(2)

    issue_client = GitHubClient(repository=cmip7_repository, token=token)
    issue_number = int(issue["number"])

    if preparation.validation_errors:
        issue_client.comment_issue(
            issue_number,
            format_validation_comment(
                preparation.validation_errors,
                preparation.notes,
            ),
        )
        typer.echo("Registration form has validation errors.")
        raise typer.Exit(0)

    prepared = preparation.prepared
    targets = _resolve_targets(
        prepared=prepared,
        cmip7_repository=cmip7_repository,
        pr_base_branch=pr_base_branch,
        cmip7_token=token,
        cmip7_client=issue_client,
        universe_repository=universe_repository,
        universe_base_branch=universe_base_branch,
    )

    action = event.get("action")
    if action not in {"opened", "edited"}:
        typer.echo(f"Ignoring unsupported issue action: {action}")
        raise typer.Exit(0)

    branch = (
        f"registration/{prepared.kind}-{issue_number}-{prepared.identifier}"
    )
    raise typer.Exit(
        _process_registration(
            action=action,
            issue_client=issue_client,
            issue_number=issue_number,
            branch=branch,
            prepared=prepared,
            targets=targets,
        )
    )


def _resolve_targets(
    *,
    prepared: PreparedRegistration,
    cmip7_repository: str,
    pr_base_branch: str,
    cmip7_token: str,
    cmip7_client: GitHubClient,
    universe_repository: str,
    universe_base_branch: str,
) -> dict[str, RepoTarget]:
    """Build a repository target for each repository the registration writes to."""
    targets: dict[str, RepoTarget] = {}
    universe_token: str | None = None
    for output in prepared.outputs:
        if output.repository in targets:
            continue
        if output.repository == cmip7_repository:
            targets[output.repository] = RepoTarget(
                client=cmip7_client, base_branch=pr_base_branch
            )
        elif output.repository == universe_repository:
            if universe_token is None:
                universe_token = os.environ.get("UNIVERSE_ACCESS_TOKEN")
            if not universe_token:
                typer.echo(
                    "The UNIVERSE_ACCESS_TOKEN environment variable must be set to "
                    f"open pull requests in `{universe_repository}`.",
                    err=True,
                )
                raise typer.Exit(2)
            targets[output.repository] = RepoTarget(
                client=GitHubClient(
                    repository=output.repository, token=universe_token
                ),
                base_branch=universe_base_branch,
            )
        else:
            typer.echo(
                f"No credentials configured for repository `{output.repository}`.",
                err=True,
            )
            raise typer.Exit(2)
    return targets


def _event_path_from_environment() -> Path:
    event_path = os.environ.get("GITHUB_EVENT_PATH")
    if not event_path:
        typer.echo("No event path supplied.", err=True)
        raise typer.Exit(2)
    return Path(event_path)


def _process_registration(
    *,
    action: str,
    issue_client: GitHubClient,
    issue_number: int,
    branch: str,
    prepared: PreparedRegistration,
    targets: dict[str, RepoTarget],
) -> int:
    """Open or update one pull request per repository the registration targets."""
    pull_requests: list[dict[str, object]] = []
    for repository, outputs in _outputs_by_repository(prepared).items():
        target = targets[repository]
        pull_requests.append(
            _sync_repository(
                action=action,
                target=target,
                issue_client=issue_client,
                issue_number=issue_number,
                branch=branch,
                outputs=outputs,
                prepared=prepared,
            )
        )

    issue_client.comment_issue(
        issue_number,
        format_success_comment(pull_requests, prepared.notes),
    )
    typer.echo(
        "Processed registration into "
        f"{len(pull_requests)} pull request(s): "
        + ", ".join(f"#{pull['number']}" for pull in pull_requests)
        + "."
    )
    return 0


def _outputs_by_repository(
    prepared: PreparedRegistration,
) -> dict[str, list[RegistrationOutput]]:
    """Group the prepared outputs by repository, preserving their order."""
    grouped: dict[str, list[RegistrationOutput]] = {}
    for output in prepared.outputs:
        grouped.setdefault(output.repository, []).append(output)
    return grouped


def _sync_repository(
    *,
    action: str,
    target: RepoTarget,
    issue_client: GitHubClient,
    issue_number: int,
    branch: str,
    outputs: list[RegistrationOutput],
    prepared: PreparedRegistration,
) -> dict[str, object]:
    """Open or update the registration pull request in a single repository."""
    if action == "opened":
        return _open_pull_request(
            target=target,
            issue_client=issue_client,
            issue_number=issue_number,
            branch=branch,
            outputs=outputs,
            prepared=prepared,
        )

    client = target.client
    pulls = client.find_pull_requests_for_branch(branch)
    if not pulls:
        pulls = client.find_pull_requests_for_issue(issue_number)

    open_pulls = [pull for pull in pulls if pull.get("state") == "open"]
    if len(open_pulls) > 1:
        pull_numbers = ", ".join(f"#{pull['number']}" for pull in open_pulls)
        message = (
            "Multiple open registration pull requests were found in "
            f"`{client.repository}` for this issue: {pull_numbers}. Please close "
            "the duplicates before editing the registration issue again."
        )
        issue_client.comment_issue(issue_number, format_edit_error_comment(message))
        raise RuntimeError(message)

    if not open_pulls:
        return _open_pull_request(
            target=target,
            issue_client=issue_client,
            issue_number=issue_number,
            branch=branch,
            outputs=outputs,
            prepared=prepared,
        )

    pull_request = open_pulls[0]
    target_branch = str(pull_request.get("head", {}).get("ref") or branch)
    for output in outputs:
        previous_output_path = _previous_output_path(
            prepared=prepared,
            issue_number=issue_number,
            branch=target_branch,
            path=output.path,
        )
        if previous_output_path and previous_output_path != output.path:
            client.delete_file(
                path=previous_output_path,
                branch=target_branch,
                message=f"Remove previous {prepared.kind} registration file",
            )

    for output in outputs:
        client.put_file(
            path=output.path,
            branch=target_branch,
            content=output.content,
            message=prepared.commit_message,
        )
    pr_number = int(pull_request["number"])
    _assign_pull_request(client, pr_number)
    typer.echo(f"Updated pull request #{pr_number} in {client.repository}.")
    return {
        "repository": client.repository,
        "number": pr_number,
        "html_url": pull_request["html_url"],
        "updated": True,
    }


def _open_pull_request(
    *,
    target: RepoTarget,
    issue_client: GitHubClient,
    issue_number: int,
    branch: str,
    outputs: list[RegistrationOutput],
    prepared: PreparedRegistration,
) -> dict[str, object]:
    """Create the registration branch, commit the files and open a pull request."""
    client = target.client
    base_branch = target.base_branch

    if not client.branch_exists(branch):
        base_sha = client.get_ref_sha(base_branch)
        client.create_branch(branch, base_sha)

    for output in outputs:
        client.put_file(
            path=output.path,
            branch=branch,
            content=output.content,
            message=prepared.commit_message,
        )

    pull_request = client.create_pull_request(
        title=prepared.pull_request_title,
        head=branch,
        base=base_branch,
        body=_pull_request_body(
            kind=prepared.kind,
            issue_number=issue_number,
            issue_repository=issue_client.repository,
            target_repository=client.repository,
        ),
    )
    pr_number = int(pull_request["number"])
    _assign_pull_request(client, pr_number)
    typer.echo(f"Created pull request #{pr_number} in {client.repository}.")
    return {
        "repository": client.repository,
        "number": pr_number,
        "html_url": pull_request["html_url"],
        "updated": False,
    }


def _pull_request_body(
    *,
    kind: str,
    issue_number: int,
    issue_repository: str,
    target_repository: str,
) -> str:
    """Build a pull request body that references the source issue.

    GitHub closing keywords only auto-close issues in the same repository, so a
    cross-repository pull request references the issue with its full slug instead.
    """
    lines = [f"Automated {kind} registration generated from #{issue_number}.", ""]
    if target_repository == issue_repository:
        lines.append(f"Closes #{issue_number}")
    else:
        lines.append(f"Generated from {issue_repository}#{issue_number}")
    return "\n".join(lines)


def _assign_pull_request(client: GitHubClient, pr_number: int) -> None:
    """Assign the reviewers to a pull request, tolerating assignment failures.

    Assignment can fail when the reviewers are not collaborators on the target
    repository (for example in the WCRP universe). That must not abort the
    registration, so the failure is logged and processing continues.
    """
    try:
        client.assign_issue(pr_number, ASSIGNEES)
    except GitHubApiError as exc:
        typer.echo(
            f"Could not assign {ASSIGNEES} to pull request #{pr_number} in "
            f"{client.repository}: {exc}",
            err=True,
        )


def _previous_output_path(
    *,
    prepared: PreparedRegistration,
    issue_number: int,
    branch: str,
    path: str,
) -> str | None:
    prefix = f"registration/{prepared.kind}-{issue_number}-"
    if not branch.startswith(prefix):
        return None
    previous_identifier = branch.removeprefix(prefix)
    if previous_identifier == prepared.identifier:
        return None
    return format_output_path_for_identifier(
        Path(path),
        previous_identifier,
    )
