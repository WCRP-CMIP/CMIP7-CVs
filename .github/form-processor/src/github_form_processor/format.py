"""Formatting helpers for registration processing."""

from __future__ import annotations

from pathlib import Path

from pydantic import ValidationError


def format_registration_title(kind: str, identifier: str) -> str:
    """Format a registration pull request title."""
    return f"Register {kind} {identifier}"


def format_registration_commit_message(kind: str, identifier: str) -> str:
    """Format a registration commit message."""
    return f"Register {kind} {identifier}"


def format_output_path(directory: str, identifier: str) -> str:
    """Format the output path for a registration identifier."""
    path = Path(directory) / f"{identifier}.json"
    return path.as_posix()


def format_output_path_for_identifier(output_path: Path, identifier: str) -> str:
    """Format an output path using a different identifier."""
    return (output_path.parent / f"{identifier}.json").as_posix()


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
    pull_requests: list[dict[str, object]],
    notes: list[str],
) -> str:
    """Format a success comment for the source issue.

    `pull_requests` is a list of mappings, one per opened or updated pull
    request, each with `repository`, `number`, `html_url` and `updated` keys.
    """
    lines: list[str] = []
    for pull_request in pull_requests:
        action = "Updated" if pull_request["updated"] else "Created"
        lines.append(
            f"{action} [pull request #{pull_request['number']}]"
            f"({pull_request['html_url']}) in `{pull_request['repository']}` "
            "for further review and iteration."
        )
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
