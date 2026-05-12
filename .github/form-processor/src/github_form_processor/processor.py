"""High-level processing for registration forms."""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Any

from pydantic import ValidationError

from github_form_processor.cv import (
    CvClient,
    UrlChecker,
    check_activity_against_cvs,
    check_activity_urls,
    check_experiment_against_cvs,
)
from github_form_processor.issue_body import parse_issue_form_body
from github_form_processor.models import ActivityRegistration, ExperimentRegistration

EXPERIMENT_LABEL = "registration: experiment"
ACTIVITY_LABEL = "registration: activity"


@dataclass(frozen=True)
class PreparedRegistration:
    """A validated registration ready to commit to a pull request."""

    kind: str
    identifier: str
    output_path: str
    content: str
    pull_request_title: str
    commit_message: str
    notes: list[str]

    def branch_name(self, issue_number: int) -> str:
        """Return the deterministic branch name for an issue registration."""
        return f"registration/{self.kind}-{issue_number}-{self.identifier}"

    def pull_request_body(self, issue_number: int) -> str:
        """Return the body for the generated pull request."""
        return (
            f"Automated {self.kind} registration generated from #{issue_number}.\n\n"
            f"Closes #{issue_number}"
        )

    def output_path_for_identifier(self, identifier: str) -> str:
        """Return the output path using a different identifier."""
        if "/" not in self.output_path:
            return f"{identifier}.json"
        directory = self.output_path.rsplit("/", maxsplit=1)[0]
        return f"{directory}/{identifier}.json"


@dataclass(frozen=True)
class RegistrationPreparationResult:
    """Result from preparing a registration issue."""

    prepared: PreparedRegistration | None
    validation_errors: list[str]
    notes: list[str]


def prepare_registration(
    *,
    issue: dict[str, Any],
    experiment_output_dir: str,
    activity_output_dir: str,
    external_checks: bool = True,
    cv_client: CvClient | None = None,
    url_checker: UrlChecker | None = None,
) -> RegistrationPreparationResult:
    """Prepare a registration from a GitHub issue payload.

    Returns
    -------
    RegistrationPreparationResult
        The prepared registration, blocking validation errors, and non-blocking
        notes. If the issue is not a recognised registration form, ``prepared``
        is ``None`` and both lists are empty. If blocking validation errors are
        found, ``prepared`` is ``None`` and ``validation_errors`` is populated.
    """
    fields = parse_issue_form_body(str(issue.get("body") or ""))
    kind = detect_form_kind(issue, fields)
    if kind is None:
        return RegistrationPreparationResult(
            prepared=None,
            validation_errors=[],
            notes=[],
        )

    notes: list[str] = []
    validation_errors: list[str] = []
    cv_client = cv_client or CvClient()
    url_checker = url_checker or UrlChecker()

    try:
        if kind == "experiment":
            experiment = _experiment_from_fields(fields)
            if (
                experiment.parent_experiment
                and experiment.parent_activity is None
            ):
                validation_errors.append(
                    "Parent activity must be supplied when parent experiment "
                    f"`{experiment.parent_experiment}` is supplied."
                )
            if external_checks:
                notes.extend(
                    check_experiment_against_cvs(
                        experiment,
                        cv_client,
                    )
                )
            prepared = PreparedRegistration(
                kind=kind,
                identifier=experiment.identifier,
                output_path=_join_output_path(
                    experiment_output_dir, experiment.identifier
                ),
                content=experiment.render_json(),
                pull_request_title=f"Register experiment {experiment.identifier}",
                commit_message=f"Register experiment {experiment.identifier}",
                notes=notes,
            )
        else:
            activity = _activity_from_fields(fields)
            if external_checks:
                validation_errors.extend(check_activity_urls(activity, url_checker))
                notes.extend(
                    check_activity_against_cvs(
                        activity,
                        cv_client,
                    )
                )
            prepared = PreparedRegistration(
                kind=kind,
                identifier=activity.identifier,
                output_path=_join_output_path(activity_output_dir, activity.identifier),
                content=activity.render_json(),
                pull_request_title=f"Register activity {activity.identifier}",
                commit_message=f"Register activity {activity.identifier}",
                notes=notes,
            )
    except ValidationError as exc:
        return RegistrationPreparationResult(
            prepared=None,
            validation_errors=_format_pydantic_errors(exc),
            notes=notes,
        )

    if validation_errors:
        return RegistrationPreparationResult(
            prepared=None,
            validation_errors=validation_errors,
            notes=notes,
        )

    return RegistrationPreparationResult(
        prepared=prepared,
        validation_errors=[],
        notes=notes,
    )


def detect_form_kind(issue: dict[str, Any], fields: dict[str, str]) -> str | None:
    """Detect whether an issue is an experiment or activity registration form."""
    labels = {str(label.get("name", "")).lower() for label in issue.get("labels", [])}
    title = str(issue.get("title", "")).lower()

    if EXPERIMENT_LABEL in labels or title.startswith("[experiment registration]"):
        return "experiment"
    if ACTIVITY_LABEL in labels or title.startswith("[activity registration]"):
        return "activity"
    if "Experiment name" in fields:
        return "experiment"
    if "Activity name" in fields:
        return "activity"
    return None


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


def _experiment_from_fields(fields: dict[str, str]) -> ExperimentRegistration:
    return ExperimentRegistration.model_validate(
        {
            "name": _require_field(fields, "Experiment name"),
            "description": _require_field(fields, "Experiment description"),
            "activity": _require_field(fields, "Activity"),
            "tier": _parse_leading_integer(_require_field(fields, "Tier")),
            "min_ensemble_size": _require_field(fields, "Minimum ensemble size"),
            "start_date": _optional_field(fields, "Start date"),
            "end_date": _optional_field(fields, "End date"),
            "min_number_yrs_per_sim": _require_field(
                fields, "Minimum number of years per simulation"
            ),
            "required_model_components": _optional_field(
                fields, "Required model components"
            ),
            "additional_allowed_model_components": _optional_field(
                fields, "Additional allowed model components"
            ),
            "parent_experiment": _optional_field(fields, "Parent experiment"),
            "parent_activity": _optional_field(fields, "Parent activity"),
            "parent_mip_era": _optional_field(fields, "Parent MIP era"),
            "branch_information": _optional_field(fields, "Branch information"),
        }
    )


def _activity_from_fields(fields: dict[str, str]) -> ActivityRegistration:
    return ActivityRegistration.model_validate(
        {
            "name": _require_field(fields, "Activity name"),
            "description": _require_field(fields, "Activity description"),
            "experiments": _optional_field(fields, "Experiments"),
            "urls": _optional_field(fields, "Reference URLs"),
        }
    )


def _require_field(fields: dict[str, str], label: str) -> str:
    value = fields.get(label, "").strip()
    if not value:
        raise ValidationError.from_exception_data(
            "Issue form",
            [
                {
                    "type": "value_error",
                    "loc": (label,),
                    "msg": "Field required",
                    "input": value,
                    "ctx": {"error": ValueError("field is required")},
                }
            ],
        )
    return value


def _optional_field(fields: dict[str, str], label: str) -> str | None:
    value = fields.get(label, "").strip()
    return value or None


def _parse_leading_integer(value: str) -> int:
    match = re.search(r"\d+", value)
    if not match:
        raise ValidationError.from_exception_data(
            "Issue form",
            [
                {
                    "type": "value_error",
                    "loc": ("Tier",),
                    "msg": "Tier must start with an integer",
                    "input": value,
                    "ctx": {"error": ValueError("tier must start with an integer")},
                }
            ],
        )
    return int(match.group(0))


def _join_output_path(directory: str, identifier: str) -> str:
    clean_directory = directory.strip("/")
    filename = f"{identifier}.json"
    if not clean_directory:
        return filename
    return f"{clean_directory}/{filename}"


def _format_pydantic_errors(error: ValidationError) -> list[str]:
    errors: list[str] = []
    for entry in error.errors():
        location = " -> ".join(str(part) for part in entry.get("loc", ())) or "form"
        message = str(entry.get("msg", "invalid value"))
        errors.append(f"{location}: {message}")
    return errors
