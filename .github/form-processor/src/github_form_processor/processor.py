"""High-level processing for registration forms."""

from __future__ import annotations

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
from github_form_processor.format import (
    format_missing_parent_activity_error,
    format_output_path,
    format_pydantic_errors,
    format_registration_commit_message,
    format_registration_title,
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
            experiment = ExperimentRegistration.from_fields(fields)
            if (
                experiment.parent_experiment
                and experiment.parent_activity is None
            ):
                validation_errors.append(
                    format_missing_parent_activity_error(
                        experiment.parent_experiment
                    )
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
                output_path=format_output_path(
                    experiment_output_dir, experiment.identifier
                ),
                content=experiment.render_json(),
                pull_request_title=format_registration_title(
                    kind, experiment.identifier
                ),
                commit_message=format_registration_commit_message(
                    kind, experiment.identifier
                ),
                notes=notes,
            )
        else:
            activity = ActivityRegistration.from_fields(fields)
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
                output_path=format_output_path(
                    activity_output_dir, activity.identifier
                ),
                content=activity.render_json(),
                pull_request_title=format_registration_title(kind, activity.identifier),
                commit_message=format_registration_commit_message(
                    kind, activity.identifier
                ),
                notes=notes,
            )
    except ValidationError as exc:
        return RegistrationPreparationResult(
            prepared=None,
            validation_errors=format_pydantic_errors(exc),
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
