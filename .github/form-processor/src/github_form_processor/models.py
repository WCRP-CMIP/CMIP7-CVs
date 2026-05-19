"""Pydantic models for registration form submissions."""

from __future__ import annotations

import json
import re
from datetime import date
from typing import Any
from urllib.parse import urlparse

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    ValidationError,
    field_validator,
    model_validator,
)

NAME_PATTERN = re.compile(r"^[A-Za-z0-9-]+$")
BLANK_VALUES = {"", "_No response_", "No response"}


class RegistrationBase(BaseModel):
    """Base model shared by registration submissions."""

    model_config = ConfigDict(extra="forbid")

    name: str
    description: str

    @property
    def identifier(self) -> str:
        """Return the lower-case identifier used in CV filenames."""
        return self.name.lower()

    @field_validator("description")
    @classmethod
    def _validate_description(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("must not be empty")
        return value


class ExperimentRegistration(RegistrationBase):
    """Validated experiment registration submission."""

    activity: str
    tier: int
    min_ensemble_size: int = 1
    start_date: date | None = None
    end_date: date | None = None
    min_number_yrs_per_sim: float
    required_model_components: list[str] = Field(default_factory=list)
    additional_allowed_model_components: list[str] = Field(default_factory=list)
    parent_experiment: str | None = None
    parent_activity: str | None = None
    parent_mip_era: str | None = None
    branch_information: str | None = None

    @classmethod
    def from_fields(cls, fields: dict[str, str]) -> ExperimentRegistration:
        """Create an experiment registration from parsed issue form fields."""
        return cls.model_validate(
            {
                "name": _require_field(fields, "Experiment name"),
                "description": _require_field(fields, "Experiment description"),
                "activity": _require_field(fields, "Activity"),
                "tier": _require_field(fields, "Tier"),
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

    @field_validator("name")
    @classmethod
    def _validate_name(cls, value: str) -> str:
        value = value.strip()
        if not NAME_PATTERN.fullmatch(value):
            raise ValueError("must contain only letters, numbers and hyphens")
        if len(value) >= 20:
            raise ValueError(
                "must be fewer than 20 characters, see https://zenodo.org/records/14929769"
            )
        return value

    @field_validator(
        "activity",
        "parent_experiment",
        "parent_activity",
        "parent_mip_era",
        mode="before",
    )
    @classmethod
    def _normalise_optional_identifier(cls, value: Any) -> str | None:
        return _normalise_optional_identifier(value)

    @field_validator("branch_information", mode="before")
    @classmethod
    def _normalise_optional_text(cls, value: Any) -> str | None:
        return _blank_to_none(value)

    @field_validator(
        "required_model_components",
        "additional_allowed_model_components",
        mode="before",
    )
    @classmethod
    def _parse_component_list(cls, value: Any) -> list[str]:
        return [_normalise_identifier(item) for item in parse_list(value)]

    @field_validator("tier")
    @classmethod
    def _validate_tier(cls, value: int) -> int:
        if value not in {1, 2, 3}:
            raise ValueError("must be 1, 2 or 3")
        return value

    @field_validator("min_ensemble_size")
    @classmethod
    def _validate_min_ensemble_size(cls, value: int) -> int:
        if value < 1:
            raise ValueError("must be a positive integer")
        return value

    @field_validator("min_number_yrs_per_sim")
    @classmethod
    def _validate_min_number_yrs_per_sim(cls, value: float) -> float:
        if value <= 0:
            raise ValueError("must be a positive number")
        return value

    @model_validator(mode="after")
    def _validate_date_span(self) -> ExperimentRegistration:
        if self.start_date is None or self.end_date is None:
            return self

        if self.end_date <= self.start_date:
            raise ValueError("end date must be after start date")

        if (self.start_date.month, self.start_date.day) != (1, 1) or (
            self.end_date.month,
            self.end_date.day,
        ) != (12, 31):
            raise NotImplementedError(
                "date-span validation only supports experiments that start on "
                "1 January and end on 31 December"
            )

        available_years = self.end_date.year - self.start_date.year + 1
        if self.min_number_yrs_per_sim > available_years:
            raise ValueError(
                "minimum number of years per simulation is longer than the interval "
                "between start date and end date"
            )

        return self

    def render_json(self) -> str:
        """Render the experiment registration as a JSON file."""
        payload: dict[str, Any] = {
            "@context": "000_context.jsonld",
            "id": self.identifier,
            "type": "experiment",
            "description": self.description,
            "drs_name": self.name,
            "start_timestamp": self.start_date.isoformat() if self.start_date else None,
            "end_timestamp": self.end_date.isoformat() if self.end_date else None,
            "activity": self.activity,
            "additional_allowed_model_components": (
                self.additional_allowed_model_components
            ),
            "branch_information": self.branch_information,
            "min_ensemble_size": self.min_ensemble_size,
            "parent_activity": self.parent_activity,
            "parent_experiment": self.parent_experiment,
            "parent_mip_era": self.parent_mip_era,
            "required_model_components": self.required_model_components,
            "tier": self.tier,
            "min_number_yrs_per_sim": self.min_number_yrs_per_sim,
        }
        return json.dumps(payload, indent=4) + "\n"


class ActivityRegistration(RegistrationBase):
    """Validated activity registration submission."""

    experiments: list[str] = Field(default_factory=list)
    urls: list[str] = Field(default_factory=list)

    @classmethod
    def from_fields(cls, fields: dict[str, str]) -> ActivityRegistration:
        """Create an activity registration from parsed issue form fields."""
        return cls.model_validate(
            {
                "name": _require_field(fields, "Activity name"),
                "description": _require_field(fields, "Activity description"),
                "experiments": _optional_field(fields, "Experiments"),
                "urls": _optional_field(fields, "Reference URLs"),
            }
        )

    @field_validator("name")
    @classmethod
    def _validate_name(cls, value: str) -> str:
        value = value.strip()
        if not NAME_PATTERN.fullmatch(value):
            raise ValueError("must contain only letters, numbers and hyphens")
        if len(value) >= 12:
            raise ValueError("must be fewer than 12 characters")
        return value

    @field_validator("experiments", mode="before")
    @classmethod
    def _parse_experiments(cls, value: Any) -> list[str]:
        return [_normalise_identifier(item) for item in parse_list(value)]

    @field_validator("urls", mode="before")
    @classmethod
    def _parse_urls(cls, value: Any) -> list[str]:
        return parse_list(value)

    @field_validator("urls")
    @classmethod
    def _validate_urls(cls, value: list[str]) -> list[str]:
        for url in value:
            parsed = urlparse(url)
            if parsed.scheme not in {"http", "https"} or not parsed.netloc:
                raise ValueError(f"`{url}` must be an HTTP or HTTPS URL")
        return value

    def render_json(self) -> str:
        """Render the activity registration as a JSON file."""
        payload: dict[str, Any] = {
            "@context": "000_context.jsonld",
            "id": self.identifier,
            "type": "activity",
            "description": self.description,
            "drs_name": self.name,
            "experiments": self.experiments,
            "urls": self.urls,
        }
        return json.dumps(payload, indent=4) + "\n"


def parse_list(value: Any) -> list[str]:
    """Parse a text area or list-like value into clean list items."""
    if value is None:
        return []
    if isinstance(value, list):
        raw_items = [str(item) for item in value]
    else:
        text = str(value).strip()
        if text in BLANK_VALUES:
            return []
        raw_items = re.split(r"[\n,]", text)

    items: list[str] = []
    for raw_item in raw_items:
        item = re.sub(r"^[-*]\s+", "", raw_item.strip())
        if item:
            items.append(item)
    return items


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


def _blank_to_none(value: Any) -> str | None:
    if value is None:
        return None
    text = str(value).strip()
    if text in BLANK_VALUES:
        return None
    return text


def _normalise_identifier(value: str) -> str:
    return value.strip().lower()


def _normalise_optional_identifier(value: Any) -> str | None:
    text = _blank_to_none(value)
    if text is None:
        return None
    return _normalise_identifier(text)
