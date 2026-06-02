"""Tests for registration models."""

import pytest
from pydantic import ValidationError

from github_form_processor.models import (
    ActivityRegistration,
    ExperimentRegistration,
    InstitutionMemberRegistration,
    InstitutionRegistration,
)


@pytest.mark.parametrize(
    ("model", "payload", "expected_message"),
    [
        (
            ExperimentRegistration,
            {
                "name": "ABCDEFGHIJKLMNOPQRSTU",
                "description": "A short experiment description.",
                "activity": "cmip",
                "tier": 1,
                "min_ensemble_size": 1,
                "min_number_yrs_per_sim": 1.0,
            },
            "Value error, must be fewer than 20 characters, see "
            "https://zenodo.org/records/14929769",
        ),
        (
            ActivityRegistration,
            {
                "name": "ABCDEFGHIJKLM",
                "description": "A short activity description.",
            },
            "Value error, must be fewer than 12 characters",
        ),
        (
            InstitutionRegistration,
            {
                "name": "ABCDEFGHIJKLMNOPQRSTU",
                "description": "A short institution description.",
            },
            "Value error, must be at most 20 characters",
        ),
        (
            InstitutionMemberRegistration,
            {
                "name": "ABCDEFGHIJKLMNOPQRSTU",
                "description": "A short member description.",
                "acronyms": ["CNRM"],
                "labels": ["Centre National de Recherches Météorologiques"],
                "ror_id": "https://ror.org/02feahw73",
            },
            "Value error, must be at most 20 characters",
        ),
    ],
)
def test_registration_name_validation_rejects_overlong_names(
    model, payload, expected_message
):
    with pytest.raises(ValidationError) as exc_info:
        model.model_validate(payload)

    error = exc_info.value.errors()[0]
    assert error["loc"] == ("name",)
    assert error["msg"] == expected_message


@pytest.mark.parametrize(
    "ror_id",
    [
        "https://ror.org/02feahw73",
        "02feahw73",
    ],
)
def test_institution_member_accepts_valid_ror_id(ror_id):
    member = InstitutionMemberRegistration.model_validate(
        {
            "name": "CNRM",
            "description": "A short member description.",
            "acronyms": ["CNRM"],
            "labels": ["Centre National de Recherches Météorologiques"],
            "ror_id": ror_id,
        }
    )
    assert member.ror_id == "https://ror.org/02feahw73"


def test_institution_member_rejects_invalid_ror_id():
    with pytest.raises(ValidationError) as exc_info:
        InstitutionMemberRegistration.model_validate(
            {
                "name": "CNRM",
                "description": "A short member description.",
                "acronyms": ["CNRM"],
                "labels": ["Centre National de Recherches Météorologiques"],
                "ror_id": "not-a-ror-id",
            }
        )

    error = exc_info.value.errors()[0]
    assert error["loc"] == ("ror_id",)
    assert "valid ROR ID" in error["msg"]


def test_institution_member_accepts_empty_acronyms_and_labels():
    member = InstitutionMemberRegistration.model_validate(
        {
            "name": "CNRM",
            "description": "A short member description.",
            "acronyms": [],
            "labels": [],
            "ror_id": "https://ror.org/02feahw73",
        }
    )

    assert member.acronyms == []
    assert member.labels == []


def test_institution_registration_name_exactly_20_chars_is_valid():
    inst = InstitutionRegistration.model_validate(
        {
            "name": "ABCDEFGHIJKLMNOPQRST",
            "description": "A short institution description.",
        }
    )
    assert inst.name == "ABCDEFGHIJKLMNOPQRST"
