"""Tests for registration preparation."""

import json

import pytest

from github_form_processor.cv import CvClient, JsonLookup, RorLookup, UrlCheck
from github_form_processor.processor import prepare_registration


class FakeRorClient:
    """Fake ROR client for deterministic tests."""

    def __init__(self, result=None):
        self.result = result or RorLookup(found=False)

    def fetch_location(self, ror_id):
        return self.result


class FakeCvClient:
    """Fake CV client for deterministic tests."""

    def __init__(self, entries):
        self.entries = entries

    def fetch_cmip7_json(self, folder, identifier):
        entry = self.entries.get(("cmip7", folder, identifier))
        if entry is None:
            return JsonLookup(found=False)
        return JsonLookup(found=True, data=entry)

    def fetch_wcrp_universe_json(self, folder, identifier):
        entry = self.entries.get(("wcrp-universe", folder, identifier))
        if entry is None:
            return JsonLookup(found=False)
        return JsonLookup(found=True, data=entry)


class FakeUrlChecker:
    """Fake URL checker for deterministic tests."""

    def __init__(self, results):
        self.results = results

    def check(self, url):
        return self.results.get(url, UrlCheck(accessible=True, status=200))


def test_prepare_experiment_registration_renders_superset_json():
    issue = {
        "title": "[Experiment registration]: Test",
        "labels": [{"name": "registration: experiment"}],
        "body": _body(
            {
                "Experiment name": "My-Experiment",
                "Experiment description": "A short experiment description.",
                "Activity": "CMIP",
                "Tier": "1",
                "Minimum ensemble size": "2",
                "Start date": "2000-01-01",
                "End date": "2010-12-31",
                "Minimum number of years per simulation": "9.5",
                "Required model components": "AOGCM",
                "Additional allowed model components": "AER\nBGC",
                "Parent experiment": "piControl",
                "Parent activity": "CMIP",
                "Parent MIP era": "cmip7",
                "Branch information": (
                    "Branch from `piControl` at a time of your choosing"
                ),
            }
        ),
    }
    cv_client = FakeCvClient(
        {
            ("cmip7", "activity", "cmip"): {"id": "cmip"},
            ("wcrp-universe", "source_type", "aogcm"): {"id": "aogcm"},
            ("wcrp-universe", "source_type", "aer"): {"id": "aer"},
            ("wcrp-universe", "source_type", "bgc"): {"id": "bgc"},
            ("wcrp-universe", "experiment", "picontrol"): {
                "id": "picontrol",
                "activity": "cmip",
            },
        }
    )

    result = prepare_registration(
        issue=issue,
        experiment_output_dir="experiment",
        activity_output_dir="activity",
        cv_client=cv_client,
    )

    assert result.validation_errors == []
    assert result.notes == []
    assert result.prepared is not None
    assert result.prepared.output_path == "experiment/my-experiment.json"
    payload = json.loads(result.prepared.content)
    assert payload == {
        "@context": "000_context.jsonld",
        "id": "my-experiment",
        "type": "experiment",
        "description": "A short experiment description.",
        "drs_name": "My-Experiment",
        "start_timestamp": "2000-01-01",
        "end_timestamp": "2010-12-31",
        "activity": "cmip",
        "additional_allowed_model_components": ["aer", "bgc"],
        "branch_information": "Branch from `piControl` at a time of your choosing",
        "min_ensemble_size": 2,
        "parent_activity": "cmip",
        "parent_experiment": "picontrol",
        "parent_mip_era": "cmip7",
        "required_model_components": ["aogcm"],
        "tier": 1,
        "min_number_yrs_per_sim": 9.5,
    }


def test_prepare_experiment_rejects_min_years_longer_than_date_span():
    issue = {
        "title": "[Experiment registration]: Test",
        "labels": [{"name": "registration: experiment"}],
        "body": _body(
            {
                "Experiment name": "My-Experiment",
                "Experiment description": "A short experiment description.",
                "Activity": "cmip",
                "Tier": "1",
                "Minimum ensemble size": "1",
                "Start date": "2000-01-01",
                "End date": "2000-12-31",
                "Minimum number of years per simulation": "2.0",
                "Required model components": "aogcm",
            }
        ),
    }

    result = prepare_registration(
        issue=issue,
        experiment_output_dir="experiment",
        activity_output_dir="activity",
        external_checks=False,
    )

    assert result.prepared is None
    assert result.notes == []
    assert any(
        "minimum number of years per simulation" in error
        for error in result.validation_errors
    )


def test_prepare_experiment_raises_for_non_calendar_year_date_span():
    issue = {
        "title": "[Experiment registration]: Test",
        "labels": [{"name": "registration: experiment"}],
        "body": _body(
            {
                "Experiment name": "My-Experiment",
                "Experiment description": "A short experiment description.",
                "Activity": "cmip",
                "Tier": "1",
                "Minimum ensemble size": "1",
                "Start date": "2000-02-01",
                "End date": "2000-12-31",
                "Minimum number of years per simulation": "1.0",
            }
        ),
    }

    with pytest.raises(NotImplementedError, match=r"1 January.*31 December"):
        prepare_registration(
            issue=issue,
            experiment_output_dir="experiment",
            activity_output_dir="activity",
            external_checks=False,
        )


def test_prepare_experiment_uses_configured_cv_client():
    issue = {
        "title": "[Experiment registration]: Test",
        "labels": [{"name": "registration: experiment"}],
        "body": _body(
            {
                "Experiment name": "My-Experiment",
                "Experiment description": "A short experiment description.",
                "Activity": "cmip",
                "Tier": "1",
                "Minimum ensemble size": "1",
                "Minimum number of years per simulation": "1.0",
                "Required model components": "aogcm",
            }
        ),
    }
    cv_client = FakeCvClient(
        {
            ("cmip7", "activity", "cmip"): {"id": "cmip"},
            ("wcrp-universe", "source_type", "aogcm"): {"id": "aogcm"},
        }
    )

    result = prepare_registration(
        issue=issue,
        experiment_output_dir="experiment",
        activity_output_dir="activity",
        cv_client=cv_client,
    )

    assert result.prepared is not None
    assert result.validation_errors == []
    assert result.notes == []


def test_prepare_experiment_errors_missing_parent_activity_with_parent_experiment():
    issue = {
        "title": "[Experiment registration]: Test",
        "labels": [{"name": "registration: experiment"}],
        "body": _body(
            {
                "Experiment name": "My-Experiment",
                "Experiment description": "A short experiment description.",
                "Activity": "cmip",
                "Tier": "1",
                "Minimum ensemble size": "1",
                "Minimum number of years per simulation": "1.0",
                "Parent experiment": "piControl",
            }
        ),
    }
    cv_client = FakeCvClient(
        {
            ("cmip7", "activity", "cmip"): {"id": "cmip"},
            ("wcrp-universe", "experiment", "picontrol"): {
                "id": "picontrol",
                "activity": "cmip",
            },
        }
    )

    result = prepare_registration(
        issue=issue,
        experiment_output_dir="experiment",
        activity_output_dir="activity",
        cv_client=cv_client,
    )

    assert result.prepared is None
    assert result.validation_errors == [
        "Parent activity must be supplied when parent experiment `picontrol` "
        "is supplied."
    ]
    assert result.notes == []


def test_prepare_experiment_notes_parent_cv_entry_missing_activity():
    issue = {
        "title": "[Experiment registration]: Test",
        "labels": [{"name": "registration: experiment"}],
        "body": _body(
            {
                "Experiment name": "My-Experiment",
                "Experiment description": "A short experiment description.",
                "Activity": "cmip",
                "Tier": "1",
                "Minimum ensemble size": "1",
                "Minimum number of years per simulation": "1.0",
                "Parent experiment": "piControl",
                "Parent activity": "CMIP",
            }
        ),
    }
    cv_client = FakeCvClient(
        {
            ("cmip7", "activity", "cmip"): {"id": "cmip"},
            ("wcrp-universe", "experiment", "picontrol"): {
                "id": "picontrol",
            },
        }
    )

    result = prepare_registration(
        issue=issue,
        experiment_output_dir="experiment",
        activity_output_dir="activity",
        cv_client=cv_client,
    )

    assert result.prepared is not None
    assert result.validation_errors == []
    assert result.notes == [
        "Could not check parent activity for parent experiment `picontrol`: "
        "parent experiment entry does not include an `activity` value."
    ]


def test_prepare_experiment_allows_missing_required_model_components():
    issue = {
        "title": "[Experiment registration]: Test",
        "labels": [{"name": "registration: experiment"}],
        "body": _body(
            {
                "Experiment name": "My-Experiment",
                "Experiment description": "A short experiment description.",
                "Activity": "cmip",
                "Tier": "1",
                "Minimum ensemble size": "1",
                "Minimum number of years per simulation": "1.0",
            }
        ),
    }

    result = prepare_registration(
        issue=issue,
        experiment_output_dir="experiment",
        activity_output_dir="activity",
        external_checks=False,
    )

    assert result.validation_errors == []
    assert result.notes == []
    assert result.prepared is not None
    assert json.loads(result.prepared.content)["required_model_components"] == []


@pytest.mark.parametrize(
    ("kind", "name_label", "name_value", "expected_error"),
    [
        (
            "experiment",
            "Experiment name",
            "ABCDEFGHIJKLMNOPQRSTU",
            "name: Value error, must be fewer than 20 characters, see "
            "https://zenodo.org/records/14929769",
        ),
        (
            "activity",
            "Activity name",
            "ABCDEFGHIJKLM",
            "name: Value error, must be fewer than 12 characters",
        ),
    ],
)
def test_prepare_registration_rejects_overlong_names(
    kind, name_label, name_value, expected_error
):
    issue = {
        "title": f"[{kind.title()} registration]: Test",
        "labels": [{"name": f"registration: {kind}"}],
        "body": _body(
            {
                name_label: name_value,
                f"{kind.title()} description": f"A short {kind} description.",
                **(
                    {
                        "Activity": "cmip",
                        "Tier": "1",
                        "Minimum ensemble size": "1",
                        "Minimum number of years per simulation": "1.0",
                    }
                    if kind == "experiment"
                    else {"Experiments": "known-exp"}
                ),
            }
        ),
    }

    result = prepare_registration(
        issue=issue,
        experiment_output_dir="experiment",
        activity_output_dir="activity",
        external_checks=False,
    )

    assert result.prepared is None
    assert result.notes == []
    assert result.validation_errors == [expected_error]


def test_prepare_activity_blocks_inaccessible_reference_url():
    issue = {
        "title": "[Activity registration]: Test",
        "labels": [{"name": "registration: activity"}],
        "body": _body(
            {
                "Activity name": "NewActivity",
                "Activity description": "A short activity description.",
                "Experiments": "known-exp\nmissing-exp",
                "Reference URLs": "https://example.invalid/dead",
            }
        ),
    }
    cv_client = FakeCvClient(
        {
            ("cmip7", "experiment", "known-exp"): {"id": "known-exp"},
        }
    )
    url_checker = FakeUrlChecker(
        {
            "https://example.invalid/dead": UrlCheck(accessible=False, status=404),
        }
    )

    result = prepare_registration(
        issue=issue,
        experiment_output_dir="experiment",
        activity_output_dir="activity",
        cv_client=cv_client,
        url_checker=url_checker,
    )

    assert result.prepared is None
    assert result.validation_errors == [
        "Reference URL `https://example.invalid/dead` returned HTTP status 404."
    ]
    assert result.notes == [
        "Experiment `missing-exp` is not already part of the CMIP7 CVs."
    ]


def test_prepare_activity_renders_json():
    issue = {
        "title": "[Activity registration]: Test",
        "labels": [{"name": "registration: activity"}],
        "body": _body(
            {
                "Activity name": "MyActivity",
                "Activity description": "A short activity description.",
                "Experiments": "- exp-one\n- exp-two",
                "Reference URLs": "https://example.com/reference",
            }
        ),
    }

    result = prepare_registration(
        issue=issue,
        experiment_output_dir="experiment",
        activity_output_dir="activity",
        external_checks=False,
    )

    assert result.validation_errors == []
    assert result.notes == []
    assert result.prepared is not None
    assert result.prepared.output_path == "activity/myactivity.json"
    assert json.loads(result.prepared.content) == {
        "@context": "000_context.jsonld",
        "id": "myactivity",
        "type": "activity",
        "description": "A short activity description.",
        "drs_name": "MyActivity",
        "experiments": ["exp-one", "exp-two"],
        "urls": ["https://example.com/reference"],
    }


def test_prepare_activity_can_check_cmip7_cvs_from_local_path(tmp_path):
    experiment_dir = tmp_path / "experiment"
    experiment_dir.mkdir()
    (experiment_dir / "known-exp.json").write_text('{"id": "known-exp"}')
    issue = {
        "title": "[Activity registration]: Test",
        "labels": [{"name": "registration: activity"}],
        "body": _body(
            {
                "Activity name": "MyActivity",
                "Activity description": "A short activity description.",
                "Experiments": "known-exp\nmissing-exp",
            }
        ),
    }

    result = prepare_registration(
        issue=issue,
        experiment_output_dir="experiment",
        activity_output_dir="activity",
        cv_client=CvClient(cmip7_cvs_path=tmp_path),
    )

    assert result.prepared is not None
    assert result.validation_errors == []
    assert result.notes == [
        "Experiment `missing-exp` is not already part of the CMIP7 CVs."
    ]


def test_prepare_institution_renders_json():
    issue = {
        "title": "[Institution registration]: Test",
        "labels": [{"name": "registration: institution"}],
        "body": _body(
            {
                "Institution DRS name": "CNRM-CERFACS",
                "Institution description": "A short institution description.",
                "Members": "cnrm\ncerfacs",
            }
        ),
    }

    result = prepare_registration(
        issue=issue,
        experiment_output_dir="experiment",
        activity_output_dir="activity",
        external_checks=False,
    )

    assert result.validation_errors == []
    assert result.notes == []
    assert result.prepared is not None
    assert result.prepared.output_path == "institution/cnrm-cerfacs.json"
    assert json.loads(result.prepared.content) == {
        "@context": "000_context.jsonld",
        "id": "cnrm-cerfacs",
        "type": "organisation",
        "drs_name": "CNRM-CERFACS",
        "members": ["cnrm", "cerfacs"],
        "description": "A short institution description.",
    }


def test_prepare_institution_notes_missing_member():
    issue = {
        "title": "[Institution registration]: Test",
        "labels": [{"name": "registration: institution"}],
        "body": _body(
            {
                "Institution DRS name": "CNRM-CERFACS",
                "Institution description": "A short institution description.",
                "Members": "cnrm\ncerfacs",
            }
        ),
    }
    cv_client = FakeCvClient(
        {
            ("wcrp-universe", "institution", "cnrm"): {"id": "cnrm"},
        }
    )

    result = prepare_registration(
        issue=issue,
        experiment_output_dir="experiment",
        activity_output_dir="activity",
        cv_client=cv_client,
    )

    assert result.prepared is not None
    assert result.validation_errors == []
    assert result.notes == [
        "Member `cerfacs` is not already part of the WCRP universe CVs."
    ]


def test_prepare_institution_member_renders_json_with_ror_location():
    issue = {
        "title": "[Institution member registration]: Test",
        "labels": [{"name": "registration: institution-member"}],
        "body": _body(
            {
                "Member DRS name": "CNRM",
                "Acronyms": "CNRM\nMétéo-France/CNRM",
                "Labels": "Centre National de Recherches Météorologiques",
                "Member description": "A short member description.",
                "Reference URLs": "https://www.cnrm.meteo.fr/",
                "ROR ID": "https://ror.org/02feahw73",
            }
        ),
    }
    ror_client = FakeRorClient(
        RorLookup(
            found=True,
            locations=[
                {
                    "city": "Toulouse",
                    "country": "France",
                    "lat": 43.6047,
                    "lon": 1.4442,
                }
            ],
        )
    )

    result = prepare_registration(
        issue=issue,
        experiment_output_dir="experiment",
        activity_output_dir="activity",
        ror_client=ror_client,
    )

    assert result.validation_errors == []
    assert result.notes == [
        "1 location auto-populated from ROR: Toulouse, France (43.6047, 1.4442)."
    ]
    assert result.prepared is not None
    assert result.prepared.output_path == "institution_member/cnrm.json"
    payload = json.loads(result.prepared.content)
    assert payload == {
        "@context": "000_context.jsonld",
        "id": "cnrm",
        "type": "institution",
        "drs_name": "CNRM",
        "acronyms": ["CNRM", "Météo-France/CNRM"],
        "labels": ["Centre National de Recherches Météorologiques"],
        "description": "A short member description.",
        "location": [
            {
                "city": "Toulouse",
                "country": "France",
                "lat": 43.6047,
                "lon": 1.4442,
            }
        ],
        "ror": "02feahw73",
        "urls": ["https://www.cnrm.meteo.fr/"],
    }


def test_prepare_institution_member_adds_ror_names_and_links_without_duplicates():
    issue = {
        "title": "[Institution member registration]: Test",
        "labels": [{"name": "registration: institution-member"}],
        "body": _body(
            {
                "Member DRS name": "CNRM",
                "Acronyms": "CNRM",
                "Labels": "Centre National de Recherches Météorologiques",
                "Member description": "A short member description.",
                "Reference URLs": "https://www.cnrm.meteo.fr/",
                "ROR ID": "https://ror.org/02feahw73",
            }
        ),
    }
    ror_client = FakeRorClient(
        RorLookup(
            found=True,
            labels=[
                "Centre National de Recherches Météorologiques",
                "National Centre for Meteorological Research",
            ],
            acronyms=["CNRM", "MF/CNRM"],
            links=[
                "https://www.cnrm.meteo.fr/",
                "https://en.wikipedia.org/wiki/CNRM",
            ],
        )
    )

    result = prepare_registration(
        issue=issue,
        experiment_output_dir="experiment",
        activity_output_dir="activity",
        ror_client=ror_client,
    )

    assert result.validation_errors == []
    assert result.notes == [
        "ROR entry `https://ror.org/02feahw73` does not include location data.",
        "1 label auto-populated from ROR: "
        "National Centre for Meteorological Research.",
        "1 acronym auto-populated from ROR: MF/CNRM.",
        "1 reference URL auto-populated from ROR: "
        "https://en.wikipedia.org/wiki/CNRM.",
    ]
    assert result.prepared is not None
    payload = json.loads(result.prepared.content)
    assert payload["labels"] == [
        "Centre National de Recherches Météorologiques",
        "National Centre for Meteorological Research",
    ]
    assert payload["acronyms"] == ["CNRM", "MF/CNRM"]
    assert payload["urls"] == [
        "https://www.cnrm.meteo.fr/",
        "https://en.wikipedia.org/wiki/CNRM",
    ]


def test_prepare_institution_member_notes_ror_not_found():
    issue = {
        "title": "[Institution member registration]: Test",
        "labels": [{"name": "registration: institution-member"}],
        "body": _body(
            {
                "Member DRS name": "CNRM",
                "Acronyms": "CNRM",
                "Labels": "Centre National de Recherches Météorologiques",
                "Member description": "A short member description.",
                "ROR ID": "https://ror.org/02feahw73",
            }
        ),
    }
    ror_client = FakeRorClient(RorLookup(found=False))

    result = prepare_registration(
        issue=issue,
        experiment_output_dir="experiment",
        activity_output_dir="activity",
        ror_client=ror_client,
    )

    assert result.validation_errors == []
    assert result.notes == [
        "ROR entry `https://ror.org/02feahw73` was not found. "
        "Metadata could not be auto-populated."
    ]
    assert result.prepared is not None
    assert json.loads(result.prepared.content)["location"] == []


def _body(fields):
    return "\n\n".join(f"### {label}\n\n{value}" for label, value in fields.items())
