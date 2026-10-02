"""Regression tests for CMIP7 metadata conflict selection."""

from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path
from types import ModuleType


def load_generator() -> ModuleType:
    script = (
        Path(__file__).resolve().parents[1]
        / "scripts"
        / "generate_c7_cv_and_universe_variables_and_known_branded_variables.py"
    )
    spec = importlib.util.spec_from_file_location("generate_c7_variables", script)
    if spec is None or spec.loader is None:
        raise ImportError(f"Could not load generator from {script}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


generator = load_generator()


def test_unreferenced_formula_terms_are_skipped() -> None:
    report = {"warnings": []}
    selected = generator.select_referenced_formula_entries(
        {
            "a": {"out_name": "a"},
            "a_time1": {"out_name": "a"},
            "a_bnds": {"out_name": "a_bnds"},
            "unused": {"out_name": "unused"},
        },
        {"lev": {"z_factors": ["a"], "z_bounds_factors": ["a_bnds"]}},
        report,
    )

    assert selected == {
        "a": {"out_name": "a"},
        "a_time1": {"out_name": "a"},
        "a_bnds": {"out_name": "a_bnds"},
    }
    assert report["unreferenced_formula_terms"] == ["unused"]
    assert report["warnings"] == [
        (
            "formula_term 'unused' is not referenced by any "
            "model_level_coordinate entry and therefore skipped"
        )
    ]


def test_unreferenced_data_coordinates_are_skipped_by_id_not_out_name() -> None:
    report = {"warnings": []}

    selected = generator.select_referenced_coordinate_entries(
        {
            "time": {"out_name": "time"},
            "timefxc": {"out_name": "time"},
            "xant": {"out_name": "xant"},
        },
        {"time"},
        report,
    )

    assert set(selected) == {"time"}
    assert report["unreferenced_data_coordinates"] == ["timefxc", "xant"]
    assert "data_coordinate 'timefxc'" in report["warnings"][0]


def test_coordinate_references_include_indirect_dimensions() -> None:
    references = generator.collect_referenced_coordinate_ids(
        [
            generator.CmorVariable(
                "mon",
                "tas",
                {"dimensions": ["longitude", "latitude", "time"]},
            )
        ],
        {"tas": {"dimensions": ["longitude", "latitude", "time"]}},
        {"alev": {"generic_level_name": "alevel"}},
        {"a": {"dimensions": "alevel"}},
        {"variable_entry": {"bounds": {"dimensions": "vertices latitude"}}},
    )

    assert {
        "alevel",
        "latitude",
        "longitude",
        "time",
        "vertices",
    } <= references


def test_latitude_and_longitude_data_variables_are_explicitly_obsolete() -> None:
    assert generator.is_obsolete_variable_identifier("lat")
    assert generator.is_obsolete_variable_identifier("lon_ti-u-hs-u")
    assert not generator.is_obsolete_variable_identifier("latitude")


def observations():
    return (
        ("K", "DReq candidate K", False),
        ("degC", "DReq candidate degC", False),
    )


def selected_values(registry) -> list[str]:
    conflict = registry.payload()["conflicts"]["units"]["tas"]
    return [item["value"] for item in conflict["candidates"] if item["use"] == 1]


def conflict_payload(selected: str | None) -> dict:
    return {
        "schema_version": 1,
        "conflicts": {
            "units": {
                "tas": {
                    "candidates": [
                        {"value": "K", "use": int(selected == "K"), "sources": []},
                        {
                            "value": "degC",
                            "use": int(selected == "degC"),
                            "sources": [],
                        },
                    ]
                }
            }
        },
    }


def test_existing_metadata_preselects_new_conflict() -> None:
    registry = generator.ConflictRegistry(
        existing_defaults={("units", "tas"): ("K", "existing Universe variable/tas")}
    )

    assert registry.resolve("tas", "units", observations()) == "K"
    assert selected_values(registry) == ["K"]
    assert not registry.unresolved
    assert (
        registry.payload()["conflicts"]["units"]["tas"]["automatic_default"]
        == "existing Universe variable/tas"
    )


def test_existing_metadata_selection_is_stable_on_second_run() -> None:
    defaults = {("units", "tas"): ("K", "existing Universe variable/tas")}
    first = generator.ConflictRegistry(existing_defaults=defaults)
    first.resolve("tas", "units", observations())
    first_payload = first.payload()

    second = generator.ConflictRegistry(first_payload, defaults)
    second.resolve("tas", "units", observations())

    assert second.payload() == first_payload
    assert not generator.conflict_file_requires_review(first_payload, second.payload())


def test_conflict_file_choice_overrides_existing_metadata() -> None:
    registry = generator.ConflictRegistry(
        conflict_payload("degC"),
        {("units", "tas"): ("K", "existing Universe variable/tas")},
    )

    assert registry.resolve("tas", "units", observations()) == "degC"
    assert selected_values(registry) == ["degC"]
    assert not registry.unresolved


def test_unselected_conflict_uses_existing_metadata_default() -> None:
    registry = generator.ConflictRegistry(
        conflict_payload(None),
        {("units", "tas"): ("K", "existing Universe variable/tas")},
    )

    assert registry.resolve("tas", "units", observations()) == "K"
    assert selected_values(registry) == ["K"]
    assert not registry.unresolved


def test_removed_explicit_choice_is_not_silently_replaced() -> None:
    previous = conflict_payload(None)
    previous["conflicts"]["units"]["tas"]["candidates"].append(
        {"value": "gone", "use": 1, "sources": []}
    )
    registry = generator.ConflictRegistry(
        previous,
        {("units", "tas"): ("K", "existing Universe variable/tas")},
    )

    registry.resolve("tas", "units", observations())
    assert selected_values(registry) == []
    assert registry.unresolved == ["units.tas"]


def test_changed_conflict_file_requires_one_review_run() -> None:
    current = conflict_payload("K")

    assert generator.conflict_file_requires_review(None, current)
    assert not generator.conflict_file_requires_review(current, current)


def test_existing_project_metadata_takes_precedence(tmp_path: Path) -> None:
    universe = tmp_path / "universe"
    project = tmp_path / "project"
    (universe / "variable").mkdir(parents=True)
    (project / "variable").mkdir(parents=True)
    (universe / "variable" / "tas.json").write_text(
        json.dumps({"id": "tas", "units": "K"}), encoding="utf-8"
    )
    (project / "variable" / "tas.json").write_text(
        json.dumps({"id": "tas", "units": "degC"}), encoding="utf-8"
    )

    defaults = generator.load_existing_conflict_defaults(universe, project)

    assert defaults[("units", "tas")] == (
        "degC",
        "existing CMIP7 variable/tas",
    )


def test_project_overlay_omits_empty_values() -> None:
    full_payload = {
        "@context": "000_context.jsonld",
        "id": "tas",
        "type": "variable",
        "description": "",
        "drs_name": "tas",
        "long_name": None,
        "standard_name": "air_temperature",
        "units": "K",
    }
    universe_payload = {
        **full_payload,
        "description": "Near-surface air temperature.",
        "long_name": "Near-Surface Air Temperature",
    }

    overlay, differences = generator.project_overlay(
        full_payload,
        universe_payload,
    )

    assert "description" not in overlay
    assert "long_name" not in overlay
    assert "description" not in differences
    assert "long_name" not in differences


def test_known_branded_universe_payload_omits_optional_empty_values() -> None:
    payload = generator.universe_base_payload(
        {
            "@context": "000_context.jsonld",
            "id": "tas_tavg-h2m-hxy-u",
            "type": "known_branded_variable",
            "description": "",
            "units": None,
            "cell_methods": "",
            "var_def_qualifier": None,
        }
    )

    assert "description" not in payload
    assert "units" not in payload
    assert "cell_methods" not in payload
    assert payload["var_def_qualifier"] is None
