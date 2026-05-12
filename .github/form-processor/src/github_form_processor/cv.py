"""CV and URL checks used by the registration processor."""

from __future__ import annotations

import json
from collections.abc import Mapping
from dataclasses import dataclass
from pathlib import Path
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.parse import quote
from urllib.request import Request, urlopen

from github_form_processor.models import ActivityRegistration, ExperimentRegistration

CMIP7_CVS_URL = "https://raw.githubusercontent.com/WCRP-CMIP/CMIP7-CVs/esgvoc"
WCRP_UNIVERSE_URL = "https://raw.githubusercontent.com/WCRP-CMIP/WCRP-universe/esgvoc"


@dataclass(frozen=True)
class JsonLookup:
    """Result from looking up one JSON CV entry."""

    found: bool
    data: Mapping[str, Any] | None = None
    error: str | None = None


@dataclass(frozen=True)
class UrlCheck:
    """Result from checking whether a URL is accessible."""

    accessible: bool
    status: int | None = None
    error: str | None = None


@dataclass(frozen=True)
class CvClient:
    """Client for reading JSON files from configured CV repositories."""

    wcrp_universe_url: str = WCRP_UNIVERSE_URL
    cmip7_cvs_url: str = CMIP7_CVS_URL
    cmip7_cvs_path: Path | None = None
    timeout: int = 15

    def fetch_cmip7_json(self, folder: str, identifier: str) -> JsonLookup:
        """Fetch a JSON CV entry from the configured CMIP7-CVs location."""
        if self.cmip7_cvs_path is not None:
            return self._fetch_local_json(self.cmip7_cvs_path, folder, identifier)

        return self._fetch_remote_json(self.cmip7_cvs_url, folder, identifier)

    def fetch_wcrp_universe_json(self, folder: str, identifier: str) -> JsonLookup:
        """Fetch a JSON CV entry from the configured WCRP universe location."""
        return self._fetch_remote_json(self.wcrp_universe_url, folder, identifier)

    def _fetch_remote_json(
        self, base_url: str, folder: str, identifier: str
    ) -> JsonLookup:
        """Fetch a JSON CV entry from a remote CV root URL."""
        url = _entry_url(base_url, folder, identifier)
        request = Request(url, headers={"User-Agent": "github-form-processor"})
        try:
            with urlopen(request, timeout=self.timeout) as response:
                payload = json.loads(response.read().decode("utf-8"))
        except HTTPError as exc:
            if exc.code == 404:
                return JsonLookup(found=False)
            return JsonLookup(found=False, error=f"HTTP {exc.code} while reading {url}")
        except (URLError, TimeoutError, json.JSONDecodeError) as exc:
            return JsonLookup(found=False, error=f"{type(exc).__name__}: {exc}")

        if not isinstance(payload, Mapping):
            return JsonLookup(found=False, error=f"Expected a JSON object at {url}")
        return JsonLookup(found=True, data=payload)

    def _fetch_local_json(self, root: Path, folder: str, identifier: str) -> JsonLookup:
        """Fetch a JSON CV entry from a local repository checkout."""
        path = root / folder / f"{identifier}.json"
        try:
            payload = json.loads(path.read_text())
        except FileNotFoundError:
            return JsonLookup(found=False)
        except (OSError, json.JSONDecodeError) as exc:
            return JsonLookup(found=False, error=f"{type(exc).__name__}: {exc}")

        if not isinstance(payload, Mapping):
            return JsonLookup(found=False, error=f"Expected a JSON object at {path}")
        return JsonLookup(found=True, data=payload)


class UrlChecker:
    """Checker for user-supplied reference URLs."""

    def __init__(self, timeout: int = 15) -> None:
        self.timeout = timeout

    def check(self, url: str) -> UrlCheck:
        """Check whether a URL returns a successful HTTP status."""
        result = self._request(url, "HEAD")
        if result.status == 405 or (not result.accessible and result.status is None):
            return self._request(url, "GET")
        return result

    def _request(self, url: str, method: str) -> UrlCheck:
        request = Request(
            url, method=method, headers={"User-Agent": "github-form-processor"}
        )
        try:
            with urlopen(request, timeout=self.timeout) as response:
                status = int(response.status)
        except HTTPError as exc:
            return UrlCheck(
                accessible=False, status=int(exc.code), error=f"HTTP {exc.code}"
            )
        except (URLError, TimeoutError) as exc:
            return UrlCheck(accessible=False, error=f"{type(exc).__name__}: {exc}")

        return UrlCheck(accessible=200 <= status < 400, status=status)


def check_experiment_against_cvs(
    experiment: ExperimentRegistration,
    cv_client: CvClient,
) -> list[str]:
    """Return non-blocking notes from checking an experiment against CVs."""
    notes: list[str] = []

    activity_lookup = cv_client.fetch_cmip7_json("activity", experiment.activity)
    _append_missing_or_error_note(
        notes,
        activity_lookup,
        f"Activity `{experiment.activity}` is not already part of the CMIP7 CVs.",
        (
            f"Could not check whether activity `{experiment.activity}` is already "
            "part of the CMIP7 CVs"
        ),
    )

    for component in sorted(
        set(
            experiment.required_model_components
            + experiment.additional_allowed_model_components
        )
    ):
        component_lookup = cv_client.fetch_wcrp_universe_json(
            "source_type",
            component,
        )
        _append_missing_or_error_note(
            notes,
            component_lookup,
            (
                f"Model component `{component}` is not already part of the WCRP "
                "universe CVs."
            ),
            (
                f"Could not check model component `{component}` against the WCRP "
                "universe CVs"
            ),
        )

    if experiment.parent_experiment:
        parent_lookup = cv_client.fetch_wcrp_universe_json(
            "experiment",
            experiment.parent_experiment,
        )
        _append_missing_or_error_note(
            notes,
            parent_lookup,
            (
                f"Parent experiment `{experiment.parent_experiment}` is not already "
                "part of the WCRP universe CVs."
            ),
            (
                f"Could not check parent experiment `{experiment.parent_experiment}` "
                "against the WCRP universe CVs"
            ),
        )
        if parent_lookup.found:
            parent_activity = (
                str(parent_lookup.data.get("activity", "")).strip().lower()
            )  # type: ignore[union-attr]
            if (
                parent_activity
                and experiment.parent_activity is not None
                and parent_activity != experiment.parent_activity
            ):
                notes.append(
                    f"Parent activity `{experiment.parent_activity}` does not match "
                    f"the parent experiment entry, which uses `{parent_activity}`."
                )

    if experiment.parent_mip_era and experiment.parent_mip_era != "cmip7":
        notes.append(f"Parent MIP era `{experiment.parent_mip_era}` is not `cmip7`.")

    return notes


def check_activity_against_cvs(
    activity: ActivityRegistration,
    cv_client: CvClient,
) -> list[str]:
    """Return non-blocking notes from checking an activity against CVs."""
    notes: list[str] = []

    for experiment_id in activity.experiments:
        experiment_lookup = cv_client.fetch_cmip7_json("experiment", experiment_id)
        _append_missing_or_error_note(
            notes,
            experiment_lookup,
            f"Experiment `{experiment_id}` is not already part of the CMIP7 CVs.",
            f"Could not check experiment `{experiment_id}` against the CMIP7 CVs",
        )

    return notes


def check_activity_urls(
    activity: ActivityRegistration, url_checker: UrlChecker
) -> list[str]:
    """Return blocking validation errors for inaccessible activity URLs."""
    errors: list[str] = []

    for url in activity.urls:
        check = url_checker.check(url)
        if check.accessible:
            continue
        if check.status is not None:
            errors.append(f"Reference URL `{url}` returned HTTP status {check.status}.")
        else:
            errors.append(f"Reference URL `{url}` could not be reached: {check.error}.")

    return errors


def _append_missing_or_error_note(
    notes: list[str],
    lookup: JsonLookup,
    missing_note: str,
    error_prefix: str,
) -> None:
    if lookup.error:
        notes.append(f"{error_prefix}: {lookup.error}.")
    elif not lookup.found:
        notes.append(missing_note)


def _entry_url(base_url: str, folder: str, identifier: str) -> str:
    return (
        f"{base_url.rstrip('/')}/"
        f"{quote(folder, safe='/')}/{quote(identifier, safe='')}.json"
    )
