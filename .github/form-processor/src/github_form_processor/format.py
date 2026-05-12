"""Formatting helpers for registration processing."""

from __future__ import annotations

from pydantic import ValidationError


def format_registration_title(kind: str, identifier: str) -> str:
    """Format a registration pull request title."""
    return f"Register {kind} {identifier}"


def format_registration_commit_message(kind: str, identifier: str) -> str:
    """Format a registration commit message."""
    return f"Register {kind} {identifier}"


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


def format_pydantic_errors(error: ValidationError) -> list[str]:
    """Format pydantic validation errors for issue comments."""
    errors: list[str] = []
    for entry in error.errors():
        location = " -> ".join(str(part) for part in entry.get("loc", ())) or "form"
        message = str(entry.get("msg", "invalid value"))
        errors.append(f"{location}: {message}")
    return errors
