"""Command-line interface for processing registration issue forms."""

from __future__ import annotations

import json
import os
from pathlib import Path

import typer

from github_form_processor.cv import CvClient
from github_form_processor.format import (
    format_edit_error_comment,
    format_output_path_for_identifier,
    format_success_comment,
    format_validation_comment,
)
from github_form_processor.github_api import GitHubClient
from github_form_processor.processor import PreparedRegistration, prepare_registration

app = typer.Typer(no_args_is_help=True)


@app.command("process")
def process_issue_form(
    event_path: Path | None = typer.Option(
        None,
        "--event-path",
        help="Path to the GitHub event JSON payload. Defaults to GITHUB_EVENT_PATH.",
    ),
    pr_base_branch: str = typer.Option(
        "esgvoc_dev",
        "--pr-base-branch",
        help="Base branch for generated pull requests.",
    ),
    experiment_output_dir: str = typer.Option(
        "experiment",
        "--experiment-output-dir",
        help="Directory for generated experiment JSON files.",
    ),
    activity_output_dir: str = typer.Option(
        "activity",
        "--activity-output-dir",
        help="Directory for generated activity JSON files.",
    ),
    institution_output_dir: str = typer.Option(
        "institution",
        "--institution-output-dir",
        help="Directory for generated institution JSON files.",
    ),
    institution_member_output_dir: str = typer.Option(
        "institution_member",
        "--institution-member-output-dir",
        help="Directory for generated institution member JSON files.",
    ),
    skip_external_checks: bool = typer.Option(
        False,
        "--skip-external-checks",
        help="Skip CV and URL checks.",
    ),
    wcrp_universe_url: str = typer.Option(
        "https://raw.githubusercontent.com/WCRP-CMIP/WCRP-universe/esgvoc",
        "--wcrp-universe-url",
        help="URL root for WCRP universe CV JSON files.",
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
    """Process one GitHub issue event into a registration pull request."""
    event_path = event_path or _event_path_from_environment()
    event = json.loads(event_path.read_text())
    issue = event.get("issue")
    if not issue:
        typer.echo("Event does not contain an issue payload.")
        raise typer.Exit(0)

    preparation = prepare_registration(
        issue=issue,
        experiment_output_dir=experiment_output_dir,
        activity_output_dir=activity_output_dir,
        institution_output_dir=institution_output_dir,
        institution_member_output_dir=institution_member_output_dir,
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
    repository = os.environ.get("GITHUB_REPOSITORY")
    if not token or not repository:
        typer.echo(
            "GITHUB_TOKEN and GITHUB_REPOSITORY environment variables must be set.",
            err=True,
        )
        raise typer.Exit(2)

    client = GitHubClient(repository=repository, token=token)
    issue_number = int(issue["number"])

    if preparation.validation_errors:
        client.comment_issue(
            issue_number,
            format_validation_comment(
                preparation.validation_errors,
                preparation.notes,
            ),
        )
        typer.echo("Registration form has validation errors.")
        raise typer.Exit(0)

    action = event.get("action")
    branch = (
        f"registration/{preparation.prepared.kind}-{issue_number}-"
        f"{preparation.prepared.identifier}"
    )

    if action == "opened":
        raise typer.Exit(
            _process_opened_issue(
                client=client,
                issue_number=issue_number,
                base_branch=pr_base_branch,
                branch=branch,
                prepared=preparation.prepared,
            )
        )

    if action == "edited":
        raise typer.Exit(
            _process_edited_issue(
                client=client,
                issue_number=issue_number,
                base_branch=pr_base_branch,
                branch=branch,
                prepared=preparation.prepared,
            )
        )

    typer.echo(f"Ignoring unsupported issue action: {action}")
    raise typer.Exit(0)


def _event_path_from_environment() -> Path:
    event_path = os.environ.get("GITHUB_EVENT_PATH")
    if not event_path:
        typer.echo("No event path supplied.", err=True)
        raise typer.Exit(2)
    return Path(event_path)


def _process_opened_issue(
    *,
    client: GitHubClient,
    issue_number: int,
    base_branch: str,
    branch: str,
    prepared: PreparedRegistration,
) -> int:
    """Create the registration branch, commit and pull request."""
    if client.content_exists(prepared.output_path, base_branch):
        message = (
            f"Target file `{prepared.output_path}` already exists on "
            f"`{base_branch}`."
        )
        client.comment_issue(
            issue_number,
            format_validation_comment([message], prepared.notes),
        )
        raise RuntimeError(message)

    if not client.branch_exists(branch):
        base_sha = client.get_ref_sha(base_branch)
        client.create_branch(branch, base_sha)

    client.put_file(
        path=prepared.output_path,
        branch=branch,
        content=prepared.content,
        message=prepared.commit_message,
    )

    pull_request = client.create_pull_request(
        title=prepared.pull_request_title,
        head=branch,
        base=base_branch,
        body=(
            f"Automated {prepared.kind} registration generated from #{issue_number}."
            f"\n\nCloses #{issue_number}"
        ),
    )
    pr_number = int(pull_request["number"])
    client.assign_issue(pr_number, ["znichollscr", "ltroussellier"])
    client.comment_issue(
        issue_number,
        format_success_comment(
            pull_request["html_url"], pr_number, prepared.notes, updated=False
        ),
    )
    typer.echo(f"Created pull request #{pr_number}.")
    return 0


def _process_edited_issue(
    *,
    client: GitHubClient,
    issue_number: int,
    base_branch: str,
    branch: str,
    prepared: PreparedRegistration,
) -> int:
    """Update the existing registration pull request for an edited issue.

    When the original `opened` event failed (for example because the form had
    validation errors), no registration pull request exists yet. In that case the
    edit is treated like a fresh submission and a new pull request is opened
    instead of raising an error.
    """
    pulls = client.find_pull_requests_for_branch(branch)
    if not pulls:
        pulls = client.find_pull_requests_for_issue(issue_number)

    open_pulls = [pull for pull in pulls if pull.get("state") == "open"]
    if len(open_pulls) > 1:
        pull_numbers = ", ".join(f"#{pull['number']}" for pull in open_pulls)
        message = (
            "Multiple open registration pull requests were found for this issue: "
            f"{pull_numbers}. Please close the duplicates before editing the "
            "registration issue again."
        )
        client.comment_issue(issue_number, format_edit_error_comment(message))
        raise RuntimeError(message)

    if not open_pulls:
        return _process_opened_issue(
            client=client,
            issue_number=issue_number,
            base_branch=base_branch,
            branch=branch,
            prepared=prepared,
        )

    pull_request = open_pulls[0]
    target_branch = str(pull_request.get("head", {}).get("ref") or branch)
    previous_output_path = _previous_output_path(
        prepared=prepared,
        issue_number=issue_number,
        branch=target_branch,
    )
    if previous_output_path and previous_output_path != prepared.output_path:
        client.delete_file(
            path=previous_output_path,
            branch=target_branch,
            message=f"Remove previous {prepared.kind} registration file",
        )

    client.put_file(
        path=prepared.output_path,
        branch=target_branch,
        content=prepared.content,
        message=prepared.commit_message,
    )
    pr_number = int(pull_request["number"])
    client.assign_issue(pr_number, ["znichollscr", "ltroussellier"])
    client.comment_issue(
        issue_number,
        format_success_comment(
            pull_request["html_url"], pr_number, prepared.notes, updated=True
        ),
    )
    typer.echo(f"Updated pull request #{pr_number}.")
    return 0


def _previous_output_path(
    *,
    prepared: PreparedRegistration,
    issue_number: int,
    branch: str,
) -> str | None:
    prefix = f"registration/{prepared.kind}-{issue_number}-"
    if not branch.startswith(prefix):
        return None
    previous_identifier = branch.removeprefix(prefix)
    if previous_identifier == prepared.identifier:
        return None
    return format_output_path_for_identifier(
        Path(prepared.output_path),
        previous_identifier,
    )
