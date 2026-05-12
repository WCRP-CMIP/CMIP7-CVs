"""Formatting helpers for registration processing."""

from __future__ import annotations

from pydantic import ValidationError


def format_branch_name(kind: str, issue_number: int, identifier: str) -> str:
    """Format the deterministic branch name for an issue registration."""
    return f"{format_branch_prefix(kind, issue_number)}{identifier}"


def format_branch_prefix(kind: str, issue_number: int) -> str:
    """Format the deterministic branch prefix for an issue registration."""
    return f"registration/{kind}-{issue_number}-"


def format_registration_title(kind: str, identifier: str) -> str:
    """Format a registration pull request title."""
    return f"Register {kind} {identifier}"


def format_registration_commit_message(kind: str, identifier: str) -> str:
    """Format a registration commit message."""
    return f"Register {kind} {identifier}"


def format_pull_request_body(kind: str, issue_number: int) -> str:
    """Format the body for a generated registration pull request."""
    return (
        f"Automated {kind} registration generated from #{issue_number}.\n\n"
        f"Closes #{issue_number}"
    )


def format_output_path(directory: str, identifier: str) -> str:
    """Format the output path for a registration identifier."""
    clean_directory = directory.strip("/")
    filename = f"{identifier}.json"
    if not clean_directory:
        return filename
    return f"{clean_directory}/{filename}"


def format_output_path_for_identifier(output_path: str, identifier: str) -> str:
    """Format an output path using a different identifier."""
    if "/" not in output_path:
        return f"{identifier}.json"
    directory = output_path.rsplit("/", maxsplit=1)[0]
    return f"{directory}/{identifier}.json"


def format_validation_comment(errors: list[str], notes: list[str] | None = None) -> str:
    """Format a validation failure comment for the source issue."""
    lines = [
        "### Registration form validation failed",
        "",
        (
            "The issue form could not be processed. Please edit the issue body "
            "and save the changes."
        ),
        "",
    ]
    lines.extend(f"- {error}" for error in errors)
    if notes:
        lines.extend(["", "Additional notes:"])
        lines.extend(f"- {note}" for note in notes)
    return "\n".join(lines)


def format_success_comment(
    pull_request_url: str,
    pull_request_number: int,
    notes: list[str],
    *,
    updated: bool,
) -> str:
    """Format a success comment for the source issue."""
    action = "Updated" if updated else "Created"
    lines = [
        f"{action} [pull request #{pull_request_number}]({pull_request_url}) "
        "for further review and iteration.",
    ]
    if notes:
        lines.extend(["", "Notes:"])
        lines.extend(f"- {note}" for note in notes)
    return "\n".join(lines)


def format_edit_error_comment(message: str) -> str:
    """Format an error comment for an edited issue that cannot update a PR."""
    return f"### Registration form processing failed\n\n{message}"


def format_missing_parent_activity_error(parent_experiment: str) -> str:
    """Format a missing parent activity validation error."""
    return (
        "Parent activity must be supplied when parent experiment "
        f"`{parent_experiment}` is supplied."
    )


def format_target_file_exists_error(output_path: str, default_branch: str) -> str:
    """Format a validation error for an existing target file."""
    return f"Target file `{output_path}` already exists on `{default_branch}`."


def format_multiple_open_pull_requests_error(pull_numbers: list[int]) -> str:
    """Format an error for duplicate open registration pull requests."""
    formatted_pull_numbers = ", ".join(f"#{number}" for number in pull_numbers)
    return (
        "Multiple open registration pull requests were found for this issue: "
        f"{formatted_pull_numbers}. Please close the duplicates before editing the "
        "registration issue again."
    )


def format_closed_registration_pull_request_error(branch: str) -> str:
    """Format an error for a closed registration pull request."""
    return (
        f"The registration pull request for branch `{branch}` exists but is closed. "
        "Please open a new registration issue."
    )


def format_missing_registration_pull_request_error(branch: str) -> str:
    """Format an error for a missing registration pull request."""
    return (
        f"No open registration pull request was found for branch `{branch}`. "
        "Please open a new registration issue."
    )


def format_remove_previous_registration_file_message(kind: str) -> str:
    """Format the commit message for deleting an old registration file."""
    return f"Remove previous {kind} registration file"


def format_created_pull_request_message(pull_request_number: int) -> str:
    """Format CLI output after creating a pull request."""
    return f"Created pull request #{pull_request_number}."


def format_updated_pull_request_message(pull_request_number: int) -> str:
    """Format CLI output after updating a pull request."""
    return f"Updated pull request #{pull_request_number}."


def format_unsupported_issue_action_message(action: object) -> str:
    """Format CLI output for an unsupported issue action."""
    return f"Ignoring unsupported issue action: {action}"


def format_missing_cmip7_activity_note(activity: str) -> str:
    """Format a note for a missing CMIP7 activity."""
    return f"Activity `{activity}` is not already part of the CMIP7 CVs."


def format_cmip7_activity_check_error_prefix(activity: str) -> str:
    """Format an error prefix for a CMIP7 activity lookup failure."""
    return (
        f"Could not check whether activity `{activity}` is already part of the "
        "CMIP7 CVs"
    )


def format_missing_wcrp_model_component_note(component: str) -> str:
    """Format a note for a missing WCRP universe model component."""
    return (
        f"Model component `{component}` is not already part of the WCRP universe "
        "CVs."
    )


def format_wcrp_model_component_check_error_prefix(component: str) -> str:
    """Format an error prefix for a WCRP universe model component lookup failure."""
    return (
        f"Could not check model component `{component}` against the WCRP universe "
        "CVs"
    )


def format_missing_wcrp_parent_experiment_note(parent_experiment: str) -> str:
    """Format a note for a missing WCRP universe parent experiment."""
    return (
        f"Parent experiment `{parent_experiment}` is not already part of the WCRP "
        "universe CVs."
    )


def format_wcrp_parent_experiment_check_error_prefix(parent_experiment: str) -> str:
    """Format an error prefix for a WCRP universe parent experiment lookup failure."""
    return (
        f"Could not check parent experiment `{parent_experiment}` against the WCRP "
        "universe CVs"
    )


def format_parent_activity_missing_note(parent_experiment: str) -> str:
    """Format a note for a parent experiment entry without an activity."""
    return (
        "Could not check parent activity for parent experiment "
        f"`{parent_experiment}`: parent experiment entry does not include an "
        "`activity` value."
    )


def format_parent_activity_mismatch_note(
    submitted_parent_activity: str,
    parent_entry_activity: str,
) -> str:
    """Format a note for mismatched parent activity values."""
    return (
        f"Parent activity `{submitted_parent_activity}` does not match the parent "
        f"experiment entry, which uses `{parent_entry_activity}`."
    )


def format_parent_mip_era_note(parent_mip_era: str) -> str:
    """Format a note for a non-CMIP7 parent MIP era."""
    return f"Parent MIP era `{parent_mip_era}` is not `cmip7`."


def format_missing_cmip7_experiment_note(experiment_id: str) -> str:
    """Format a note for a missing CMIP7 experiment."""
    return f"Experiment `{experiment_id}` is not already part of the CMIP7 CVs."


def format_cmip7_experiment_check_error_prefix(experiment_id: str) -> str:
    """Format an error prefix for a CMIP7 experiment lookup failure."""
    return f"Could not check experiment `{experiment_id}` against the CMIP7 CVs"


def format_reference_url_status_error(url: str, status: int) -> str:
    """Format a blocking error for an inaccessible reference URL status."""
    return f"Reference URL `{url}` returned HTTP status {status}."


def format_reference_url_unreachable_error(url: str, error: str | None) -> str:
    """Format a blocking error for an unreachable reference URL."""
    return f"Reference URL `{url}` could not be reached: {error}."


def format_lookup_error_note(error_prefix: str, error: str) -> str:
    """Format a note for a failed lookup."""
    return f"{error_prefix}: {error}."


def format_pydantic_errors(error: ValidationError) -> list[str]:
    """Format pydantic validation errors for issue comments."""
    errors: list[str] = []
    for entry in error.errors():
        location = " -> ".join(str(part) for part in entry.get("loc", ())) or "form"
        message = str(entry.get("msg", "invalid value"))
        errors.append(f"{location}: {message}")
    return errors
