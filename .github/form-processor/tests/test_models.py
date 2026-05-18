"""Tests for registration models."""

import pytest
from pydantic import ValidationError

from github_form_processor.models import ActivityRegistration, ExperimentRegistration


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
