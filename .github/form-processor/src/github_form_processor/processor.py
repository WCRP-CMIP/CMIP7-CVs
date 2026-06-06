"""High-level processing for registration forms."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from pydantic import ValidationError

from github_form_processor.cv import (
    CvClient,
    RorClient,
    RorLookup,
    UrlChecker,
    check_activity_against_cvs,
    check_activity_urls,
    check_experiment_against_cvs,
    check_institution_against_cvs,
)
from github_form_processor.format import (
    format_output_path,
    format_pydantic_errors,
    format_registration_commit_message,
    format_registration_title,
)
from github_form_processor.issue_body import parse_issue_form_body
from github_form_processor.models import (
    ActivityRegistration,
    ExperimentRegistration,
    InstitutionMemberRegistration,
    InstitutionRegistration,
    Location,
)

EXPERIMENT_LABEL = "registration: experiment"
ACTIVITY_LABEL = "registration: activity"
INSTITUTION_LABEL = "registration: institution"
INSTITUTION_MEMBER_LABEL = "registration: institution-member"


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
    institution_output_dir: str = "institution",
    institution_member_output_dir: str = "institution_member",
    external_checks: bool = True,
    cv_client: CvClient | None = None,
    url_checker: UrlChecker | None = None,
    ror_client: RorClient | None = None,
) -> RegistrationPreparationResult:
    """Prepare a registration from a GitHub issue payload.

    Returns a `RegistrationPreparationResult` with the prepared registration,
    blocking validation errors, and non-blocking notes. If the issue is not a
    recognised registration form, `prepared` is `None` and both lists are empty.
    If blocking validation errors are found, `prepared` is `None` and
    `validation_errors` is populated.
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
    ror_client = ror_client or RorClient()

    try:
        if kind == "experiment":
            experiment = ExperimentRegistration.from_fields(fields)
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
        elif kind == "activity":
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
        elif kind == "institution":
            institution = InstitutionRegistration.from_fields(fields)
            if external_checks:
                notes.extend(check_institution_against_cvs(institution, cv_client))
            prepared = PreparedRegistration(
                kind=kind,
                identifier=institution.identifier,
                output_path=format_output_path(
                    institution_output_dir, institution.identifier
                ),
                content=institution.render_json(),
                pull_request_title=format_registration_title(
                    kind, institution.identifier
                ),
                commit_message=format_registration_commit_message(
                    kind, institution.identifier
                ),
                notes=notes,
            )
        elif kind == "institution-member":
            member = InstitutionMemberRegistration.from_fields(fields)
            if external_checks:
                ror_lookup = ror_client.fetch_location(member.ror_id)
                if ror_lookup.error:
                    notes.append(
                        f"Could not fetch metadata from ROR entry "
                        f"`{member.ror_id}`: {ror_lookup.error}."
                    )
                elif not ror_lookup.found:
                    notes.append(
                        f"ROR entry `{member.ror_id}` was not found. "
                        "Metadata could not be auto-populated."
                    )
                else:
                    member, ror_notes = _apply_ror_metadata(member, ror_lookup)
                    notes.extend(ror_notes)
            prepared = PreparedRegistration(
                kind=kind,
                identifier=member.identifier,
                output_path=format_output_path(
                    institution_member_output_dir, member.identifier
                ),
                content=member.render_json(),
                pull_request_title=format_registration_title(
                    kind, member.identifier
                ),
                commit_message=format_registration_commit_message(
                    kind, member.identifier
                ),
                notes=notes,
            )
        else:
            raise AssertionError(f"Unexpected registration kind: {kind!r}")
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


def _pluralise(count: int, noun: str) -> str:
    """Return `count` followed by `noun`, pluralised when not one."""
    return f"{count} {noun}" if count == 1 else f"{count} {noun}s"


def _new_items(candidates: list[str], existing: list[str]) -> list[str]:
    """Return `candidates` not already in `existing`, without duplicates."""
    new_items: list[str] = []
    for item in candidates:
        if item not in existing and item not in new_items:
            new_items.append(item)
    return new_items


def _apply_ror_metadata(
    member: InstitutionMemberRegistration, ror_lookup: RorLookup
) -> tuple[InstitutionMemberRegistration, list[str]]:
    """Auto-populate member metadata from a found ROR entry.

    Adds the ROR locations, and any ROR names and links the user did not
    already supply. ROR names are routed by type: acronym names extend the
    acronyms, while label and alias names extend the labels. ROR links extend
    the reference URLs. Returns the updated member and any non-blocking notes
    describing what was added.
    """
    notes: list[str] = []
    updates: dict[str, Any] = {}

    if ror_lookup.locations:
        updates["locations"] = [
            Location(
                city=loc["city"],
                country=loc["country"],
                lat=loc["lat"],
                lon=loc["lon"],
            )
            for loc in ror_lookup.locations
        ]
        loc_strs = "; ".join(
            f"{loc['city']}, {loc['country']} ({loc['lat']}, {loc['lon']})"
            for loc in ror_lookup.locations
        )
        notes.append(
            f"{_pluralise(len(ror_lookup.locations), 'location')} "
            f"auto-populated from ROR: {loc_strs}."
        )
    else:
        notes.append(
            f"ROR entry `{member.ror_id}` does not include location data."
        )

    new_labels = _new_items(ror_lookup.labels, member.labels)
    if new_labels:
        updates["labels"] = [*member.labels, *new_labels]
        notes.append(
            f"{_pluralise(len(new_labels), 'label')} auto-populated from ROR: "
            f"{', '.join(new_labels)}."
        )

    new_acronyms = _new_items(ror_lookup.acronyms, member.acronyms)
    if new_acronyms:
        updates["acronyms"] = [*member.acronyms, *new_acronyms]
        notes.append(
            f"{_pluralise(len(new_acronyms), 'acronym')} auto-populated from "
            f"ROR: {', '.join(new_acronyms)}."
        )

    new_urls = _new_items(ror_lookup.links, member.urls)
    if new_urls:
        updates["urls"] = [*member.urls, *new_urls]
        notes.append(
            f"{_pluralise(len(new_urls), 'reference URL')} auto-populated from "
            f"ROR: {', '.join(new_urls)}."
        )

    if updates:
        member = member.model_copy(update=updates)
    return member, notes


def detect_form_kind(issue: dict[str, Any], fields: dict[str, str]) -> str | None:
    """Detect whether an issue is a known registration form."""
    labels = {str(label.get("name", "")).lower() for label in issue.get("labels", [])}
    title = str(issue.get("title", "")).lower()

    if EXPERIMENT_LABEL in labels or title.startswith("[experiment registration]"):
        return "experiment"
    if ACTIVITY_LABEL in labels or title.startswith("[activity registration]"):
        return "activity"
    if INSTITUTION_MEMBER_LABEL in labels or title.startswith(
        "[institution member registration]"
    ):
        return "institution-member"
    if INSTITUTION_LABEL in labels or title.startswith("[institution registration]"):
        return "institution"
    if "Experiment name" in fields:
        return "experiment"
    if "Activity name" in fields:
        return "activity"
    if "Member DRS name" in fields:
        return "institution-member"
    if "Institution DRS name" in fields:
        return "institution"
    return None
