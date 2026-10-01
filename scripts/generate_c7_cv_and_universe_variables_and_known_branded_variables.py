"""Generate CMIP7 and related WCRP-universe JSON-LD entries.

CMIP7 Data Request metadata is the primary source for variables, known branded
variables, and coordinates.  The CMIP7 CMOR tables supplement it with the
operational coordinate definitions, formula terms, grid descriptors, flags,
and table membership required by CMOR.

Existing Universe terms are deliberately immutable.  When a term already
exists, differences from the generated CMIP7 definition are written only to
the CMIP7 project overlay.  This makes repeated runs safe while projects are
integrated sequentially into the shared Universe.
"""

from __future__ import annotations

import argparse
import json
import re
from collections.abc import Iterable
from dataclasses import dataclass
from itertools import pairwise
from pathlib import Path
from typing import Any

import data_request_api.content.dreq_content as dc
import data_request_api.query.dreq_query as dq

DEFAULT_DREQ_VERSION = "v1.2.2.5"
UNIVERSE_BASE = "https://esgvoc.ipsl.fr/resource/universe"
KNOWN_BRANDED_VARIABLE_HISTORY = "registered"

# These fields describe a project's concrete request and are intentionally not
# placed in a newly created Universe term.
PROJECT_ONLY_FIELDS = {
    "flag_meanings",
    "flag_values",
    "cell_measures",
    "comment",
    "valid_min",
    "valid_max",
    "tolerance",
    "long_name",
    "realm",
    "table_id",
    "compound_name",
}
KNOWN_BRANDED_VARIABLE_PROJECT_ONLY_FIELDS = {"description", "frequency"}

# Optional fields whose schema accepts a non-empty string or no value. Source
# tables commonly represent the latter as ""; omit those values from emitted
# JSON rather than relying on consumers to treat an empty string like null.
OPTIONAL_NON_EMPTY_TEXT_FIELDS = {
    "data_coordinate": {
        "long_name",
        "cf_standard_name",
        "units",
        "positive",
        "stored_direction",
        "coordinate_values",
    },
    "formula_term": {"long_name", "cf_standard_name", "units"},
    "grid_axis": {
        "axis",
        "data_type",
        "long_name",
        "cf_standard_name",
        "out_name",
        "units",
    },
    "grid_variable": {"long_name", "cf_standard_name"},
    "model_level_coordinate": {
        "long_name",
        "cf_standard_name",
        "computed_standard_name",
        "units",
        "formula",
    },
    "known_branded_variable": {
        "long_name",
        "units",
        "realm",
        "cell_methods",
        "cell_measures",
        "var_def_qualifier",
        "bn_status",
        "cf_sn_status",
        "history",
    },
}

COORDINATE_TYPES = {
    "standard_1d": (
        "1-D coordinate variable whose name matches its dimension. The most common type. "
        "Examples include plev19, time, and spectral-band coordinates. Parametric vertical "
        "coordinates with formulas also use this type. QA/QC verifies the coordinate variable, "
        "matching dimension, units, requested values, bounds, and formula terms when specified."
    ),
    "scalar": (
        "Single-valued coordinate listed in the coordinates attribute rather than used as a "
        "dimension. Its value may be numeric or character. QA/QC verifies the requested value, "
        "the coordinates attribute, and requested bounds when specified."
    ),
    "auxiliary": (
        "Auxiliary 1-D coordinate with a simple index dimension. Values are character labels "
        "identifying categories. QA/QC verifies that the character coordinate variable exists "
        "and is associated with the expected index dimension."
    ),
    "generic_vertical": (
        "Abstract model-level vertical coordinate whose values are model-dependent. QA/QC "
        "verifies a dimension with output name 'lev' without requiring specific level values. "
        "Concrete model-level coordinates reference it through generic_level_name."
    ),
    "generic_horizontal": (
        "Longitude or latitude used as a generic horizontal coordinate. It may be a regular "
        "1-D coordinate or be represented by grid indices and auxiliary geographic variables. "
        "The axis field distinguishes X from Y."
    ),
    "site": (
        "Site or station index dimension with longitude and latitude supplied as auxiliary "
        "coordinates. QA/QC verifies the geographic auxiliary coordinates and dimension length."
    ),
}

GENERIC_LEVEL_METADATA = {
    "alevel": (
        "Atmospheric Model Level",
        (
            "Generic atmospheric model vertical coordinate (nondimensional or dimensional). Use "
            "the CF standard name appropriate for the model vertical coordinate, for example "
            "model_level_number or atmosphere_sigma_coordinate."
        ),
    ),
    "alevhalf": (
        "Atmospheric Model Half-level",
        (
            "Generic atmospheric model vertical half-level coordinate (nondimensional or dimensional)."
            " Use the CF standard name appropriate for the model vertical coordinate, for example "
            "model_level_number or atmosphere_sigma_coordinate."
        ),
    ),
    "olevel": (
        "Ocean Model Level",
        (
            "Generic ocean model vertical coordinate (nondimensional or dimensional). "
            "Use the CF standard name appropriate for the model vertical coordinate."
        ),
    ),
    "olevhalf": (
        "Ocean Model Half Level",
        (
            "Generic ocean model vertical half-level coordinate (nondimensional or dimensional). "
            "Use the CF standard name appropriate for the model vertical coordinate."
        ),
    ),
}

DESCRIPTOR_REFERENCES = {
    "data_coordinate": {"coordinate_type": "coordinate_type"},
    "formula_term": {"dimensions": "data_coordinate"},
    "grid_variable": {"dimensions": "data_coordinate"},
    "model_level_coordinate": {
        "generic_level_name": "data_coordinate",
        "z_factors": "formula_term",
        "z_bounds_factors": "formula_term",
    },
    "known_branded_variable": {
        "variable_root_name": "variable",
        "dimensions": "data_coordinate",
        "temporal_label": "temporal_label",
        "vertical_label": "vertical_label",
        "horizontal_label": "horizontal_label",
        "area_label": "area_label",
        "realm": "realm",
        "table_id": "table",
        "frequency": "frequency",
    },
}

# JSON-LD predicates identify properties, not the collections containing their
# referenced values. These two fields target the same collection and therefore
# need distinct predicates to prevent their expanded values from colliding.
REFERENCE_PROPERTY_IDS = {
    ("model_level_coordinate", "z_factors"): f"{UNIVERSE_BASE}/z_factors",
    ("model_level_coordinate", "z_bounds_factors"): f"{UNIVERSE_BASE}/z_bounds_factors",
}

PROJECT_COLLECTIONS = {
    "data_coordinate": "data_coordinate",
    "formula_term": "formula_term",
    "grid_axis": "grid_axis",
    "grid_variable": "grid_variable",
    "known_branded_variable": "branded_variable",
    "model_level_coordinate": "model_level_coordinate",
    "table": "table",
    "variable": "variable",
    "frequency": "frequency",
}


@dataclass(frozen=True)
class CmorVariable:
    table_id: str
    variable_entry: str
    entry: dict[str, Any]


def parse_args() -> argparse.Namespace:
    script_dir = Path(__file__).resolve().parent
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repos-base-dir", type=Path, default=script_dir.parents[1])
    parser.add_argument("--cmip7-cmor-tables-dir", type=Path)
    parser.add_argument("--wcrp-universe-dir", type=Path)
    parser.add_argument("--cmip7-cv-dir", type=Path)
    parser.add_argument("--dreq-version", default=DEFAULT_DREQ_VERSION)
    parser.add_argument(
        "--conflicts-path",
        type=Path,
        default=script_dir / "CMIP7_conflicts.json",
        help="Persistent user-editable selections for CMIP7 metadata conflicts.",
    )
    parser.add_argument(
        "--offline",
        action=argparse.BooleanOptionalAction,
        default=True,
        help="Use the locally cached Data Request (default: true).",
    )
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument(
        "--report-path",
        type=Path,
        default=script_dir / "c7_cv_universe_overlay_report.json",
    )
    return parser.parse_args()


def resolve_paths(args: argparse.Namespace) -> dict[str, Path]:
    base = args.repos_base_dir
    cmor_repo = args.cmip7_cmor_tables_dir or base / "cmip7-cmor-tables"
    return {
        "cmor": cmor_repo / "tables",
        "universe": args.wcrp_universe_dir or base / "WCRP-universe",
        "project": args.cmip7_cv_dir or base / "CMIP7-CVs",
    }


def read_json(path: Path) -> dict[str, Any]:
    with path.open(encoding="utf-8") as handle:
        return json.load(handle)


def read_json_if_exists(path: Path) -> dict[str, Any] | None:
    return read_json(path) if path.exists() else None


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        json.dump(payload, handle, indent=4, ensure_ascii=False)
        handle.write("\n")


def is_empty(value: Any) -> bool:
    if value is None:
        return True
    if isinstance(value, str):
        return not value.strip()
    if isinstance(value, (list, tuple, set, dict)):
        return not value
    return False


def optional_text(value: Any) -> str | None:
    if value is None:
        return None
    if isinstance(value, (list, tuple, set)):
        value = " ".join(str(item) for item in value if not is_empty(item))
    return str(value).strip() or None


def clean_text(value: Any) -> str | None:
    text = optional_text(value)
    if text is None:
        return None
    text = re.sub(r"\\([_/%#&{}$])", r"\1", text)
    return re.sub(r"\\(?![nrt\"\\/bfu])", "", text)


def as_list(value: Any) -> list[Any]:
    if is_empty(value):
        return []
    if isinstance(value, (list, tuple, set)):
        return list(value)
    return [value]


def split_words(value: Any) -> list[str]:
    result: list[str] = []
    for item in as_list(value):
        for word in re.split(r"[,\s]+", str(item).strip()):
            if word and word not in result:
                result.append(word)
    return result


def unique(values: Iterable[str]) -> list[str]:
    return list(dict.fromkeys(value for value in values if value))


def add_optional(payload: dict[str, Any], key: str, value: Any) -> None:
    if not is_empty(value):
        payload[key] = value


def omit_blank_optional_text(
    descriptor: str, payload: dict[str, Any]
) -> dict[str, Any]:
    """Omit blank strings where the descriptor schema permits absence."""
    normalized = dict(payload)
    for field_name in OPTIONAL_NON_EMPTY_TEXT_FIELDS.get(descriptor, set()):
        value = normalized.get(field_name)
        if isinstance(value, str) and not value.strip():
            normalized.pop(field_name)
    return normalized


def parse_number(value: Any, data_type: str) -> int | float:
    number = float(value)
    if data_type == "integer":
        if not number.is_integer():
            raise ValueError(f"Expected integer value, got {value!r}")
        return int(number)
    return number


def parse_numeric_values(value: Any, data_type: str) -> list[int | float] | None:
    words = split_words(value)
    return [parse_number(word, data_type) for word in words] if words else None


def parse_optional_float(value: Any) -> float | None:
    return None if is_empty(value) else float(value)


def bool_or_none(value: Any) -> bool | None:
    if is_empty(value):
        return None
    if isinstance(value, bool):
        return value
    text = str(value).strip().lower()
    if text in {"yes", "true", "1", "y"}:
        return True
    if text in {"no", "false", "0", "n"}:
        return False
    raise ValueError(f"Expected a boolean-like value, got {value!r}")


def get_attr(record: Any, key: str, default: Any = None) -> Any:
    return getattr(record, key, default) if record is not None else default


def get_first_record(table: Any, links: Any) -> Any | None:
    values = as_list(links)
    return table.get_record(values[0]) if values else None


def get_linked_values(table: Any, links: Any, fields: tuple[str, ...]) -> list[str]:
    result: list[str] = []
    for link in as_list(links):
        record = table.get_record(link)
        for field in fields:
            value = clean_text(get_attr(record, field))
            if value:
                if value not in result:
                    result.append(value)
                break
    return result


def build_context(descriptor: str, *, include_vocab: bool) -> dict[str, Any]:
    """Build a context; only the Universe layer owns the fallback vocabulary."""
    references = DESCRIPTOR_REFERENCES.get(descriptor, {})
    context: dict[str, Any] = {"@base": f"{UNIVERSE_BASE}/{descriptor}/"}
    if include_vocab:
        context["@vocab"] = "http://schema.org/"
    context.update(
        {
            "id": "@id",
            "type": "@type",
            descriptor: f"{UNIVERSE_BASE}/{descriptor}/",
        }
    )
    for field_name, target in references.items():
        context[field_name] = {
            "@id": REFERENCE_PROPERTY_IDS.get(
                (descriptor, field_name), f"{UNIVERSE_BASE}/{target}/"
            ),
            "@type": "@id",
            "@context": {"@base": f"{UNIVERSE_BASE}/{target}/"},
        }
    payload: dict[str, Any] = {"@context": context}
    if references:
        payload["esgvoc_resolve_modes"] = dict.fromkeys(references, "full")
    return payload


def emit(
    path: Path,
    payload: dict[str, Any],
    *,
    dry_run: bool,
    report: dict[str, Any],
    category: str,
) -> None:
    existing = read_json_if_exists(path)
    if existing == payload:
        return
    action = "created" if existing is None else "updated"
    report[f"{action}_entries"].setdefault(category, []).append(path.stem)
    if not dry_run:
        write_json(path, payload)


def universe_base_payload(full_payload: dict[str, Any]) -> dict[str, Any]:
    excluded = set(PROJECT_ONLY_FIELDS)
    is_known_branded_variable = full_payload.get("type") == "known_branded_variable"
    if is_known_branded_variable:
        excluded.update(KNOWN_BRANDED_VARIABLE_PROJECT_ONLY_FIELDS)
    return {
        key: value
        for key, value in full_payload.items()
        if key not in excluded
        and (
            not is_known_branded_variable
            or key == "var_def_qualifier"
            or not is_empty(value)
        )
    }


def preserve_existing_universe_payload(
    candidate: dict[str, Any], existing: dict[str, Any] | None
) -> dict[str, Any]:
    """Keep every existing Universe value exactly as it was."""
    return candidate if existing is None else existing


def project_overlay(
    full_payload: dict[str, Any], universe_payload: dict[str, Any]
) -> tuple[dict[str, Any], dict[str, dict[str, Any]]]:
    identity = ("@context", "id", "type")
    overlay = {key: full_payload[key] for key in identity if key in full_payload}
    differences: dict[str, dict[str, Any]] = {}
    for key, project_value in full_payload.items():
        if key in identity:
            continue
        # Project files are sparse overlays. Missing source metadata must
        # inherit from the Universe rather than mask it with null/blank values.
        if is_empty(project_value):
            continue
        universe_value = universe_payload.get(key)
        is_known_project_field = (
            full_payload.get("type") == "known_branded_variable"
            and key in KNOWN_BRANDED_VARIABLE_PROJECT_ONLY_FIELDS
        )
        if (
            key in PROJECT_ONLY_FIELDS
            or is_known_project_field
            or project_value != universe_value
        ):
            overlay[key] = project_value
            differences[key] = {
                "universe": universe_value,
                "cmip7": project_value,
            }
    return overlay, differences


def validate_payload(descriptor: str, payload: dict[str, Any]) -> None:
    from pydantic import TypeAdapter

    from esgvoc.api.pydantic_handler import get_pydantic_class

    TypeAdapter(get_pydantic_class(descriptor)).validate_python(payload)


def emit_layered_payload(
    descriptor: str,
    full_payload: dict[str, Any],
    universe_root: Path,
    project_root: Path,
    *,
    dry_run: bool,
    report: dict[str, Any],
) -> None:
    full_payload = omit_blank_optional_text(descriptor, full_payload)
    identifier = str(full_payload["id"]).lower()
    validate_payload(descriptor, full_payload)
    universe_path = universe_root / descriptor / f"{identifier}.json"
    existing_universe = read_json_if_exists(universe_path)
    if (
        descriptor == "known_branded_variable"
        and existing_universe is None
        and full_payload.get("history") != KNOWN_BRANDED_VARIABLE_HISTORY
    ):
        raise ValueError(
            f"New Universe known branded variable {identifier!r} must have history "
            f"{KNOWN_BRANDED_VARIABLE_HISTORY!r}"
        )
    universe_payload = preserve_existing_universe_payload(
        universe_base_payload(full_payload), existing_universe
    )
    if existing_universe is None:
        validate_payload(descriptor, universe_payload)
    emit(
        universe_path,
        universe_payload,
        dry_run=dry_run,
        report=report,
        category=f"universe_{descriptor}",
    )
    overlay, differences = project_overlay(full_payload, universe_payload)
    report["overlay_differences"].setdefault(descriptor, {})[identifier] = differences
    emit(
        project_root / PROJECT_COLLECTIONS[descriptor] / f"{identifier}.json",
        overlay,
        dry_run=dry_run,
        report=report,
        category=f"project_{descriptor}",
    )


def generate_contexts(
    universe_root: Path,
    project_root: Path,
    *,
    dry_run: bool,
    report: dict[str, Any],
) -> None:
    universe_descriptors = {
        "coordinate_type",
        "data_coordinate",
        "formula_term",
        "grid_axis",
        "grid_variable",
        "model_level_coordinate",
        "known_branded_variable",
        "table",
        "variable",
    }
    for descriptor in sorted(universe_descriptors):
        emit(
            universe_root / descriptor / "000_context.jsonld",
            build_context(descriptor, include_vocab=True),
            dry_run=dry_run,
            report=report,
            category=f"universe_{descriptor}_context",
        )
    for descriptor, collection in sorted(PROJECT_COLLECTIONS.items()):
        emit(
            project_root / collection / "000_context.jsonld",
            build_context(descriptor, include_vocab=False),
            dry_run=dry_run,
            report=report,
            category=f"project_{collection}_context",
        )


def load_dreq_tables(version: str, offline: bool) -> Any:
    """Load one cached or remotely retrieved CMIP7 Data Request release."""
    if not offline:
        dc.retrieve(version)
    content = dc.load(version, offline=offline)
    return dq.create_dreq_tables_for_request(content, version)


def load_cmor_variables(cmor_dir: Path) -> list[CmorVariable]:
    records: list[CmorVariable] = []
    excluded = {
        "coordinate",
        "formula_terms",
        "grids",
        "cell_measures",
        "long_name_overrides",
        "CV",
    }
    for table_path in sorted(cmor_dir.glob("CMIP7_*.json")):
        table_id = table_path.stem.removeprefix("CMIP7_")
        if table_id in excluded:
            continue
        content = read_json(table_path)
        entries = content.get("variable_entry")
        if not isinstance(entries, dict) or not content.get("Header"):
            continue
        for variable_entry, entry in entries.items():
            records.append(CmorVariable(table_id, variable_entry, dict(entry)))
    return records


def load_table_payloads(cmor_dir: Path) -> dict[str, dict[str, Any]]:
    payloads: dict[str, dict[str, Any]] = {}
    for record in load_cmor_variables(cmor_dir):
        payloads.setdefault(record.table_id, {})[record.variable_entry] = record.entry
    result: dict[str, dict[str, Any]] = {}
    for table_id, entries in payloads.items():
        document = read_json(cmor_dir / f"CMIP7_{table_id}.json")
        header = document["Header"]
        result[table_id] = {
            "@context": "000_context.jsonld",
            "id": table_id.lower(),
            "type": "table",
            "description": f"CMIP7 {table_id} CMOR table.",
            "drs_name": table_id,
            "product": optional_text(header.get("product")),
            "table_date": optional_text(header.get("table_date")),
            "variable_entry": sorted(entries),
        }
    return result


def merge_dreq_coordinate_records(
    table: Any, report: dict[str, Any]
) -> dict[str, dict[str, Any]]:
    """Merge duplicate DReq coordinate names without inventing combined values."""
    result: dict[str, dict[str, Any]] = {}
    for record in table.records.values():
        identifier = optional_text(get_attr(record, "name"))
        if identifier is None:
            report["warnings"].append("Skipped a DReq coordinate without a name")
            continue
        incoming = dict(record.__dict__)
        if identifier not in result:
            result[identifier] = incoming
            continue
        existing = result[identifier]
        for key, value in incoming.items():
            if is_empty(existing.get(key)) and not is_empty(value):
                existing[key] = value
            elif not is_empty(value) and existing.get(key) != value:
                warning = (
                    f"DReq coordinate {identifier!r} has conflicting {key}; "
                    "keeping the first non-empty value"
                )
                if warning not in report["warnings"]:
                    report["warnings"].append(warning)
    return result


def first_nonempty(*values: Any) -> Any:
    return next((value for value in values if not is_empty(value)), None)


def coordinate_source_value(
    dreq_entry: dict[str, Any] | None,
    cmor_entry: dict[str, Any] | None,
    dreq_keys: tuple[str, ...],
    cmor_keys: tuple[str, ...],
) -> Any:
    dreq_entry = dreq_entry or {}
    cmor_entry = cmor_entry or {}
    return first_nonempty(
        *(dreq_entry.get(key) for key in dreq_keys),
        *(cmor_entry.get(key) for key in cmor_keys),
    )


def normalize_requested_bounds(
    bounds: list[int | float] | None,
    requested_value_count: int,
) -> list[int | float] | None:
    """Convert CMOR's paired bounds to the model's flat ``m + 1`` edge vector."""
    if bounds is None or len(bounds) <= 2:
        return bounds
    if requested_value_count and len(bounds) == requested_value_count + 1:
        return bounds
    if len(bounds) % 2:
        return bounds
    pairs = list(zip(bounds[::2], bounds[1::2], strict=True))
    if all(left[1] == right[0] for left, right in pairwise(pairs)):
        return [pairs[0][0], *(upper for _, upper in pairs)]
    return bounds


def classify_coordinate(
    identifier: str,
    data_type: str,
    values: list[Any] | str | None,
    bounds: list[Any] | None,
) -> str:
    value_count = 1 if isinstance(values, str) else len(values or [])
    if value_count == 1 or len(bounds or []) == 2:
        return "scalar"
    if data_type == "character":
        return "auxiliary"
    if identifier in {"latitude", "longitude"}:
        return "generic_horizontal"
    if identifier == "site":
        return "site"
    return "standard_1d"


def build_generic_coordinate_payload(
    identifier: str, dreq_entry: dict[str, Any] | None = None
) -> dict[str, Any]:
    default_long_name, default_description = GENERIC_LEVEL_METADATA[identifier]
    entry = dreq_entry or {}
    return {
        "@context": "000_context.jsonld",
        "id": identifier,
        "type": "data_coordinate",
        "description": clean_text(entry.get("description")) or default_description,
        "drs_name": identifier,
        "coordinate_type": "generic_vertical",
        "axis": "Z",
        "data_type": "double",
        "long_name": clean_text(entry.get("title")) or default_long_name,
        "out_name": clean_text(entry.get("output_name")) or "lev",
        "is_climatology": False,
        "is_generic_model_level_coordinate": True,
    }


def build_vertices_coordinate_payload() -> dict[str, Any]:
    return {
        "@context": "000_context.jsonld",
        "id": "vertices",
        "type": "data_coordinate",
        "description": "Index dimension enumerating the vertices of a grid cell.",
        "drs_name": "vertices",
        "coordinate_type": "standard_1d",
        "data_type": "integer",
        "long_name": "Grid Cell Vertex Index",
        "out_name": "vertices",
        "units": "1",
        "is_climatology": False,
        "is_generic_model_level_coordinate": False,
    }


def build_data_coordinate_payload(
    identifier: str,
    dreq_entry: dict[str, Any] | None,
    cmor_entry: dict[str, Any] | None,
) -> dict[str, Any]:
    if identifier in GENERIC_LEVEL_METADATA:
        return build_generic_coordinate_payload(identifier, dreq_entry)

    data_type = str(
        coordinate_source_value(dreq_entry, cmor_entry, ("type",), ("type",))
        or "double"
    ).lower()
    raw_values = coordinate_source_value(
        dreq_entry,
        cmor_entry,
        ("value_scalar_or_string", "requested_values"),
        ("value", "requested"),
    )
    raw_bounds = coordinate_source_value(
        dreq_entry,
        cmor_entry,
        ("bounds_scalar", "requested_bounds"),
        ("bounds_values", "requested_bounds"),
    )
    values: list[int | float | str] | str | None
    bounds: list[int | float] | None = None
    if data_type == "character":
        parsed = split_words(raw_values)
        values = parsed[0] if len(parsed) == 1 else parsed or None
    else:
        values = parse_numeric_values(raw_values, data_type)
        bounds = parse_numeric_values(raw_bounds, data_type)
        bounds = normalize_requested_bounds(bounds, len(values or []))

    payload: dict[str, Any] = {
        "@context": "000_context.jsonld",
        "id": identifier.lower(),
        "type": "data_coordinate",
        "description": clean_text((dreq_entry or {}).get("description")) or "",
        "drs_name": identifier,
        "coordinate_type": classify_coordinate(identifier, data_type, values, bounds),
        "data_type": data_type,
        "long_name": coordinate_source_value(
            dreq_entry, cmor_entry, ("title",), ("long_name",)
        ),
        "out_name": coordinate_source_value(
            dreq_entry, cmor_entry, ("output_name",), ("out_name",)
        )
        or identifier,
    }
    for target, dreq_keys, cmor_keys in (
        ("cf_standard_name", ("cf_standard_name",), ("standard_name",)),
        ("units", ("units",), ("units",)),
        ("axis", ("axis_flag",), ("axis",)),
        ("positive", ("positive_direction",), ("positive",)),
        ("stored_direction", ("stored_direction",), ("stored_direction",)),
    ):
        add_optional(
            payload,
            target,
            coordinate_source_value(dreq_entry, cmor_entry, dreq_keys, cmor_keys),
        )
    if values is not None:
        payload["coordinate_values"] = values
    if bounds is not None:
        payload["coordinate_bounds"] = bounds

    bounds_required = bool_or_none(
        coordinate_source_value(
            dreq_entry,
            cmor_entry,
            ("bounds_flag",),
            ("must_have_bounds",),
        )
    )
    if bounds_required is not None:
        payload["bounds_required"] = bounds_required
    climatology = bool_or_none(
        coordinate_source_value(
            dreq_entry,
            cmor_entry,
            ("climatology_flag",),
            ("climatology",),
        )
    )
    payload["is_climatology"] = bool(climatology)
    payload["is_generic_model_level_coordinate"] = False

    if data_type != "character":
        valid_min = parse_optional_float(
            coordinate_source_value(
                dreq_entry,
                cmor_entry,
                ("minimum_valid_value",),
                ("valid_min",),
            )
        )
        valid_max = parse_optional_float(
            coordinate_source_value(
                dreq_entry,
                cmor_entry,
                ("maximum_valid_value",),
                ("valid_max",),
            )
        )
        if valid_min is not None:
            payload["valid_min"] = valid_min
        if valid_max is not None:
            payload["valid_max"] = valid_max
        tolerance = parse_optional_float(
            coordinate_source_value(
                dreq_entry, cmor_entry, ("tolerance",), ("tolerance",)
            )
        )
        value_count = (
            len(values or []) if isinstance(values, list) else int(values is not None)
        )
        if tolerance is not None and (value_count > 1 or len(bounds or []) > 2):
            payload["tolerance"] = tolerance
    return payload


def parse_formula_term_references(
    value: Any,
    formula_term_ids: set[str],
    *,
    generic_level_name: str,
    coordinate_out_name: str,
    bounds: bool,
) -> list[str] | None:
    """Resolve CMOR ``term: variable`` mappings to FormulaTerm IDs."""
    text = optional_text(value)
    if text is None:
        return None
    pairs = re.findall(r"(?:^|\s)([^:\s]+):\s*([^\s]+)", text)
    references: list[str] = []
    for term, variable in pairs:
        # The coordinate itself can be a CF formula term (for example
        # ``sigma: lev``). It is represented by ModelLevelCoordinate and must
        # not also be emitted as a FormulaTerm reference.
        expected_coordinate_name = (
            f"{coordinate_out_name}_bnds" if bounds else coordinate_out_name
        )
        if variable.lower() == expected_coordinate_name.lower():
            continue
        candidates: list[str] = []
        if generic_level_name.endswith("half"):
            candidates.append(f"{term}_half")
        if bounds:
            candidates.extend((variable, f"{term}_bnds"))
        candidates.extend((variable, term))
        resolved = next(
            (
                candidate.lower()
                for candidate in candidates
                if candidate.lower() in formula_term_ids
            ),
            None,
        )
        if resolved is None:
            raise ValueError(
                f"Formula mapping {term!r}: {variable!r} cannot be resolved to a formula term"
            )
        references.append(resolved)
    return unique(references) or None


def build_model_level_payload(
    identifier: str,
    entry: dict[str, Any],
    formula_term_ids: set[str],
) -> dict[str, Any]:
    generic_level_name = str(entry.get("generic_level_name", "")).lower()
    coordinate_out_name = optional_text(entry.get("out_name")) or identifier
    positive = optional_text(entry.get("positive"))
    stored_direction = optional_text(entry.get("stored_direction"))
    if positive is None and generic_level_name.startswith("olev"):
        positive = "up"
    if stored_direction is None and generic_level_name.startswith("olev"):
        stored_direction = "decreasing"
    payload: dict[str, Any] = {
        "@context": "000_context.jsonld",
        "id": identifier.lower(),
        "type": "model_level_coordinate",
        "description": optional_text(entry.get("description")) or "",
        "drs_name": identifier,
        "axis": "Z",
        "data_type": optional_text(entry.get("type")) or "double",
        "long_name": optional_text(entry.get("long_name")),
        "out_name": coordinate_out_name,
        "positive": positive,
        "stored_direction": stored_direction,
        "generic_level_name": generic_level_name,
    }
    for source, target in (
        ("standard_name", "cf_standard_name"),
        ("computed_standard_name", "computed_standard_name"),
        ("units", "units"),
        ("formula", "formula"),
    ):
        add_optional(payload, target, optional_text(entry.get(source)))
    for source in ("z_factors", "z_bounds_factors"):
        references = parse_formula_term_references(
            entry.get(source),
            formula_term_ids,
            generic_level_name=generic_level_name,
            coordinate_out_name=coordinate_out_name,
            bounds=source == "z_bounds_factors",
        )
        if references:
            payload[source] = references
    bounds_required = bool_or_none(entry.get("must_have_bounds"))
    if bounds_required is not None:
        payload["bounds_required"] = bounds_required
    for key in ("valid_min", "valid_max"):
        value = parse_optional_float(entry.get(key))
        if value is not None:
            payload[key] = value
    return payload


def build_formula_term_payload(
    identifier: str, entry: dict[str, Any]
) -> dict[str, Any]:
    payload: dict[str, Any] = {
        "@context": "000_context.jsonld",
        "id": identifier.lower(),
        "type": "formula_term",
        "description": optional_text(entry.get("description")) or "",
        "drs_name": identifier,
        "data_type": optional_text(entry.get("type")) or "double",
        "long_name": optional_text(entry.get("long_name")),
        "out_name": optional_text(entry.get("out_name")) or identifier,
    }
    add_optional(payload, "cf_standard_name", optional_text(entry.get("standard_name")))
    add_optional(payload, "units", optional_text(entry.get("units")))
    dimensions = [value.lower() for value in split_words(entry.get("dimensions"))]
    if dimensions:
        payload["dimensions"] = dimensions
    return payload


def build_grid_axis_payload(identifier: str, entry: dict[str, Any]) -> dict[str, Any]:
    payload: dict[str, Any] = {
        "@context": "000_context.jsonld",
        "id": identifier.lower(),
        "type": "grid_axis",
        "description": optional_text(entry.get("description")) or "",
        "drs_name": identifier,
    }
    for source, target in (
        ("axis", "axis"),
        ("type", "data_type"),
        ("long_name", "long_name"),
        ("standard_name", "cf_standard_name"),
        ("out_name", "out_name"),
        ("units", "units"),
    ):
        add_optional(payload, target, optional_text(entry.get(source)))
    return payload


def build_grid_variable_payload(
    identifier: str, entry: dict[str, Any]
) -> dict[str, Any]:
    payload: dict[str, Any] = {
        "@context": "000_context.jsonld",
        "id": identifier.lower(),
        "type": "grid_variable",
        "description": optional_text(entry.get("description")) or "",
        "drs_name": identifier,
        "data_type": optional_text(entry.get("type")) or "double",
        "out_name": optional_text(entry.get("out_name")) or identifier,
        "units": optional_text(entry.get("units")) or "1",
        "dimensions": [value.lower() for value in split_words(entry.get("dimensions"))],
    }
    add_optional(payload, "long_name", optional_text(entry.get("long_name")))
    add_optional(payload, "cf_standard_name", optional_text(entry.get("standard_name")))
    for key in ("valid_min", "valid_max"):
        value = parse_optional_float(entry.get(key))
        if value is not None:
            payload[key] = value
    return payload


def split_branded_name(branded_name: str) -> tuple[str, str, str, str, str, str]:
    if "_" not in branded_name:
        raise ValueError(f"Invalid branded variable name {branded_name!r}")
    root_name, suffix = branded_name.split("_", 1)
    parts = suffix.split("-")
    if len(parts) < 4:
        raise ValueError(
            f"Branded variable {branded_name!r} does not contain four suffix labels"
        )
    return root_name, suffix, parts[0], parts[1], parts[2], "-".join(parts[3:])


def resolve_dimension_name(coordinate_table: Any, token: str) -> str:
    try:
        record = coordinate_table.get_record(token)
    except Exception:  # noqa: BLE001 - plain names are expected here too.
        if "record=" in token:
            record_id = re.split(r"[,\s]+", token.split("record=", 1)[1])[0]
            try:
                record = coordinate_table.get_record(record_id)
            except Exception:  # noqa: BLE001
                return token
        else:
            return token
    return optional_text(get_attr(record, "name")) or token


def get_dimensions(var: Any, coordinate_table: Any) -> list[str]:
    return unique(
        resolve_dimension_name(coordinate_table, token).lower()
        for token in split_words(get_attr(var, "dimensions"))
    )


def resolve_primary_realm(var: Any, realm_table: Any) -> str | None:
    values = get_linked_values(
        realm_table,
        get_attr(var, "modelling_realm___primary"),
        ("id", "name"),
    )
    return values[0].lower() if values else None


def resolve_standard_name(
    var: Any, cf_table: Any, physical_parameter: Any
) -> str | None:
    values = get_linked_values(
        cf_table,
        get_attr(var, "cf_standard_name_from_physical_parameter"),
        ("name",),
    )
    if not values and physical_parameter is not None:
        values = get_linked_values(
            cf_table,
            get_attr(physical_parameter, "cf_standard_name"),
            ("name",),
        )
    return values[0] if values else None


def resolve_linked_text(table: Any, links: Any, fields: tuple[str, ...]) -> str | None:
    values = get_linked_values(table, links, fields)
    return values[0] if values else None


def cmor_records_by_branded_name(
    records: list[CmorVariable],
) -> dict[str, list[CmorVariable]]:
    result: dict[str, list[CmorVariable]] = {}
    for record in records:
        result.setdefault(record.variable_entry.lower(), []).append(record)
    return result


def dreq_records_by_branded_name(variable_table: Any) -> dict[str, list[Any]]:
    result: dict[str, list[Any]] = {}
    for var in variable_table.records.values():
        branded_name = optional_text(get_attr(var, "branded_variable_name"))
        if branded_name:
            result.setdefault(branded_name.lower(), []).append(var)
    return result


VARIABLE_CONFLICT_FIELDS = (
    "drs_name",
    "long_name",
    "standard_name",
    "units",
    # Keep descriptions last in the field-first file: there can be hundreds
    # of harmless, automatically resolved description alternatives, and they
    # should not obscure metadata conflicts that need human attention.
    "description",
)

CONFLICT_FIELD_ORDER = (
    "drs_name",
    "cf_standard_name",
    "standard_name",
    "units",
    "dimensions",
    "cell_methods",
    "cell_measures",
    "realm",
    "out_name",
    "long_name",
    # Descriptions are intentionally last because this usually is by far the
    # largest automatically resolved section.
    "description",
)


EXISTING_CONFLICT_FIELDS = {
    "variable": VARIABLE_CONFLICT_FIELDS,
    "known_branded_variable": (
        "dimensions",
        "cf_standard_name",
        "units",
        "out_name",
        "cell_methods",
    ),
}


def load_existing_conflict_defaults(
    universe_root: Path, project_root: Path
) -> dict[tuple[str, str], tuple[Any, str]]:
    """Load canonical conflict defaults from resolved project metadata."""
    defaults: dict[tuple[str, str], tuple[Any, str]] = {}
    for descriptor, fields in EXISTING_CONFLICT_FIELDS.items():
        universe_dir = universe_root / descriptor
        project_collection = PROJECT_COLLECTIONS[descriptor]
        project_dir = project_root / project_collection
        identifiers = {
            path.stem
            for directory in (universe_dir, project_dir)
            if directory.is_dir()
            for path in directory.glob("*.json")
        }
        for identifier in sorted(identifiers):
            universe_payload = read_json_if_exists(
                universe_dir / f"{identifier}.json"
            ) or {}
            project_payload = read_json_if_exists(
                project_dir / f"{identifier}.json"
            ) or {}
            for field in fields:
                if field in project_payload and not is_empty(project_payload[field]):
                    defaults[(field, identifier.lower())] = (
                        project_payload[field],
                        f"existing CMIP7 {project_collection}/{identifier}",
                    )
                elif field in universe_payload and not is_empty(
                    universe_payload[field]
                ):
                    defaults[(field, identifier.lower())] = (
                        universe_payload[field],
                        f"existing Universe {descriptor}/{identifier}",
                    )
    return defaults


def variable_observation(
    identifier: str,
    drs_name: str,
    var: Any,
    physical: Any,
    tables: Any,
    *,
    source: str,
    preferred: bool,
) -> dict[str, Any]:
    """Return one sourced proposal for a Variable term."""
    standard_name = resolve_standard_name(var, tables["CF Standard Names"], physical)
    units = first_nonempty(
        *as_list(get_attr(var, "units_from_physical_parameter")),
        get_attr(physical, "units"),
    )
    return {
        "id": identifier.lower(),
        "source": source,
        "preferred": preferred,
        "values": {
            "description": clean_text(get_attr(physical, "description"))
            or clean_text(get_attr(var, "description"))
            or "",
            "drs_name": drs_name,
            "long_name": clean_text(get_attr(physical, "title"))
            or clean_text(get_attr(var, "title")),
            "standard_name": standard_name,
            "units": optional_text(units) or "1",
        },
    }


def previous_conflict_selections(
    payload: dict[str, Any] | None,
) -> tuple[
    set[tuple[str, str]],
    dict[tuple[str, str], list[Any]],
    dict[tuple[str, str], str],
]:
    """Return known conflict records and the values previously marked for use."""
    known: set[tuple[str, str]] = set()
    selected: dict[tuple[str, str], list[Any]] = {}
    automatic_defaults: dict[tuple[str, str], str] = {}
    conflicts = (payload or {}).get("conflicts", {})
    if not isinstance(conflicts, dict):
        return known, selected, automatic_defaults
    for field, terms in conflicts.items():
        if not isinstance(terms, dict):
            continue
        for identifier, conflict in terms.items():
            key = (str(field), str(identifier).lower())
            known.add(key)
            candidates = (
                conflict.get("candidates", []) if isinstance(conflict, dict) else []
            )
            selected[key] = [
                candidate.get("value")
                for candidate in candidates
                if isinstance(candidate, dict) and candidate.get("use") == 1
            ]
            automatic_default = (
                conflict.get("automatic_default")
                if isinstance(conflict, dict)
                else None
            )
            if isinstance(automatic_default, str):
                automatic_defaults[key] = automatic_default
    return known, selected, automatic_defaults


class ConflictRegistry:
    """Collect persistent conflicts with existing metadata as reviewable defaults."""

    def __init__(
        self,
        previous_payload: dict[str, Any] | None = None,
        existing_defaults: dict[tuple[str, str], tuple[Any, str]] | None = None,
    ):
        (
            self.known,
            self.previous_selections,
            self.previous_automatic_defaults,
        ) = previous_conflict_selections(previous_payload)
        self.existing_defaults = existing_defaults or {}
        self.conflicts: dict[str, dict[str, dict[str, Any]]] = {}
        self.unresolved: list[str] = []

    def resolve(
        self,
        identifier: str,
        field: str,
        observations: Iterable[tuple[Any, str, bool]],
        *,
        default: Any = None,
        automatic: str | None = None,
    ) -> Any:
        """Resolve observations, recording alternatives when values differ."""
        sources_by_value: dict[str, dict[str, Any]] = {}
        preferred_values: set[str] = set()
        for value, source, preferred in observations:
            if is_empty(value):
                continue
            serialized = json.dumps(value, ensure_ascii=False, sort_keys=True)
            item = sources_by_value.setdefault(
                serialized,
                {"value": value, "sources": []},
            )
            if source not in item["sources"]:
                item["sources"].append(source)
            if preferred:
                preferred_values.add(serialized)

        candidates = [
            sources_by_value[key] for key in sorted(sources_by_value, key=str.casefold)
        ]
        if not candidates:
            return default
        if len(candidates) == 1:
            return candidates[0]["value"]

        conflict_key = (field, identifier.lower())
        previously_selected = self.previous_selections.get(conflict_key, [])
        has_previous_selection = bool(previously_selected)
        selected_serialized = {
            serialized
            for value in previously_selected
            if (serialized := json.dumps(value, ensure_ascii=False, sort_keys=True))
            in sources_by_value
        }
        automatic_default = (
            self.previous_automatic_defaults.get(conflict_key, automatic)
            if has_previous_selection
            else automatic
        )
        if not has_previous_selection:
            existing = self.existing_defaults.get(conflict_key)
            if existing is not None:
                existing_value, existing_source = existing
                serialized = json.dumps(
                    existing_value, ensure_ascii=False, sort_keys=True
                )
                if serialized in sources_by_value:
                    selected_serialized = {serialized}
                    automatic_default = existing_source

        if not has_previous_selection and not selected_serialized:
            if automatic == "longest":
                longest = max(
                    candidates,
                    key=lambda candidate: len(str(candidate["value"])),
                )
                selected_serialized = {
                    json.dumps(longest["value"], ensure_ascii=False, sort_keys=True)
                }
            elif len(preferred_values) == 1:
                selected_serialized = set(preferred_values)

        conflict_candidates = []
        for candidate in candidates:
            serialized = json.dumps(
                candidate["value"], ensure_ascii=False, sort_keys=True
            )
            conflict_candidates.append(
                {
                    "value": candidate["value"],
                    "use": int(serialized in selected_serialized),
                    "sources": sorted(candidate["sources"]),
                }
            )
        conflict_record: dict[str, Any] = {"candidates": conflict_candidates}
        if automatic_default is not None:
            conflict_record["automatic_default"] = automatic_default
        self.conflicts.setdefault(field, {})[identifier.lower()] = conflict_record

        selected_candidates = [
            candidate for candidate in conflict_candidates if candidate["use"] == 1
        ]
        if len(selected_candidates) == 1:
            return selected_candidates[0]["value"]
        self.unresolved.append(f"{field}.{identifier.lower()}")
        # Keep constructing the complete preflight payload so conflicts in
        # later descriptors are discovered in the same run. This provisional
        # value is never emitted while any unresolved selection remains.
        return candidates[0]["value"]

    def payload(self) -> dict[str, Any]:
        """Return the stable field-first JSON representation."""
        ordered_fields = [
            *CONFLICT_FIELD_ORDER,
            *(field for field in self.conflicts if field not in CONFLICT_FIELD_ORDER),
        ]
        return {
            "schema_version": 1,
            "conflicts": {
                field: self.conflicts[field]
                for field in ordered_fields
                if field in self.conflicts
            },
        }


def conflict_file_requires_review(
    previous_payload: dict[str, Any] | None, current_payload: dict[str, Any]
) -> bool:
    """Require review whenever a non-empty conflict file changed this run."""
    return bool(current_payload.get("conflicts")) and previous_payload != current_payload


def build_cmip7_variable_payloads(
    dreq_by_branded: dict[str, list[Any]],
    tables: Any,
    conflicts: ConflictRegistry,
    report: dict[str, Any],
) -> tuple[dict[str, dict[str, Any]], set[str]]:
    """Build the union of branded roots and referenced Physical Parameters."""
    observations: dict[str, list[dict[str, Any]]] = {}
    root_ids: set[str] = set()
    root_physical_pairs: set[tuple[str, str]] = set()

    for records in dreq_by_branded.values():
        for var in records:
            branded_name = optional_text(get_attr(var, "branded_variable_name"))
            if branded_name is None:
                continue
            root_name = branded_name.split("_", 1)[0]
            root_id = root_name.lower()
            root_ids.add(root_id)
            physical = get_first_record(
                tables["Physical Parameters"], get_attr(var, "physical_parameter")
            )
            physical_name = clean_text(get_attr(physical, "name"))
            if physical_name is None:
                raise ValueError(
                    f"CMIP7 variable {branded_name!r} has no named Physical Parameter"
                )
            physical_id = physical_name.lower()
            root_physical_pairs.add((root_name, physical_name))
            source = f"Variables/{branded_name} -> Physical Parameters/{physical_name}"
            same_name = root_id == physical_id
            observations.setdefault(root_id, []).append(
                variable_observation(
                    root_id,
                    root_name,
                    var,
                    physical,
                    tables,
                    source=source,
                    preferred=same_name,
                )
            )
            observations.setdefault(physical_id, []).append(
                variable_observation(
                    physical_id,
                    physical_name,
                    var,
                    physical,
                    tables,
                    source=source,
                    preferred=True,
                )
            )

    variable_payloads: dict[str, dict[str, Any]] = {}

    for identifier, proposals in sorted(observations.items()):
        resolved_values: dict[str, Any] = {}
        for field in VARIABLE_CONFLICT_FIELDS:
            resolved_values[field] = conflicts.resolve(
                identifier,
                field,
                (
                    (
                        proposal["values"].get(field),
                        proposal["source"],
                        proposal["preferred"],
                    )
                    for proposal in proposals
                ),
                default="" if field == "description" else None,
                automatic="longest" if field == "description" else None,
            )
        variable_payloads[identifier] = {
            "@context": "000_context.jsonld",
            "id": identifier,
            "type": "variable",
            **resolved_values,
        }

    differing_pairs = sorted(
        [
            {"root_name": root, "physical_parameter_name": physical}
            for root, physical in root_physical_pairs
            if root.lower() != physical.lower()
        ],
        key=lambda pair: (
            pair["root_name"].lower(),
            pair["physical_parameter_name"].lower(),
        ),
    )
    report["root_physical_parameter_pairs"] = {
        "different_name_count": len(differing_pairs),
        "pairs": differing_pairs,
    }
    return variable_payloads, root_ids


def parse_flag_values(value: Any) -> list[int] | None:
    values = split_words(value)
    if not values:
        return None
    return [int(item) for item in values]


def build_known_payload(
    identifier: str,
    dreq_records: list[Any],
    cmor_records: list[CmorVariable],
    root_payload: dict[str, Any],
    tables: Any,
    cmor_cell_measures: dict[str, str],
    conflicts: ConflictRegistry,
) -> dict[str, Any]:
    first = dreq_records[0]
    branded_name = optional_text(get_attr(first, "branded_variable_name")) or identifier
    root_name, suffix, temporal, vertical, horizontal, area = split_branded_name(
        branded_name
    )
    standard_names: list[str] = []
    units_values: list[str] = []
    dimensions_values: list[list[str]] = []
    cell_methods_values: list[str] = []
    cell_measures_values: list[str] = []
    realm_values: list[str] = []
    comments: list[str] = []
    long_names: list[str] = []
    compounds: list[str] = []
    frequency_values: list[str] = []

    for var in dreq_records:
        physical = get_first_record(
            tables["Physical Parameters"], get_attr(var, "physical_parameter")
        )
        standard_name = resolve_standard_name(
            var, tables["CF Standard Names"], physical
        )
        if standard_name:
            standard_names.append(standard_name)
        units = first_nonempty(
            *as_list(get_attr(var, "units_from_physical_parameter")),
            get_attr(physical, "units"),
        )
        if not is_empty(units):
            units_values.append(str(units))
        dimensions = get_dimensions(var, tables["Coordinates and Dimensions"])
        if dimensions:
            dimensions_values.append(dimensions)
        cell_methods = resolve_linked_text(
            tables["Cell Methods"], get_attr(var, "cell_methods"), ("cell_methods",)
        )
        if cell_methods:
            cell_methods_values.append(cell_methods)
        cell_measures = resolve_linked_text(
            tables["Cell Measures"], get_attr(var, "cell_measures"), ("name",)
        )
        compound_name = optional_text(get_attr(var, "cmip7_compound_name"))
        if compound_name:
            compounds.append(compound_name)
            add_measure = optional_text(cmor_cell_measures.get(compound_name))
            if add_measure:
                cell_measures_values.append(add_measure)
        if cell_measures:
            cell_measures_values.append(cell_measures)
        realm = resolve_primary_realm(var, tables["Modelling Realm"])
        if realm:
            realm_values.append(realm)
        frequency_values.extend(
            get_linked_values(
                tables["CMIP7 Frequency"],
                get_attr(var, "cmip7_frequency"),
                ("name",),
            )
        )
        comment = clean_text(get_attr(var, "description"))
        if comment:
            comments.append(comment)
        long_name = clean_text(get_attr(var, "title"))
        if long_name:
            long_names.append(long_name)

    def sourced_values(
        dreq_values: Iterable[Any],
        cmor_key: str | None = None,
        *,
        cmor_transform=optional_text,
    ) -> list[tuple[Any, str, bool]]:
        observations = [
            (
                value,
                f"CMIP7 Data Request Variables/{branded_name} candidate {index}",
                False,
            )
            for index, value in enumerate(dreq_values, start=1)
        ]
        if cmor_key is not None:
            observations.extend(
                (
                    cmor_transform(record.entry.get(cmor_key)),
                    f"CMIP7 CMOR {record.table_id}.{record.variable_entry}",
                    False,
                )
                for record in cmor_records
            )
        return observations

    for record in cmor_records:
        if comment := clean_text(record.entry.get("comment")):
            comments.append(comment)
        if long_name := clean_text(record.entry.get("long_name")):
            long_names.append(long_name)
        if cell_measure := optional_text(record.entry.get("cell_measures")):
            cell_measures_values.append(cell_measure)
        realm_values.extend(
            realm.lower()
            for realm in split_words(record.entry.get("modeling_realm"))
        )

    comments = unique(comments)
    long_names = unique(long_names)
    cell_measures_values = unique(cell_measures_values)
    realm_values = unique(realm_values)
    frequencies = unique(
        [
            *(frequency.lower() for frequency in frequency_values),
            *(
                frequency.lower()
                for record in cmor_records
                for frequency in split_words(record.entry.get("frequency"))
            ),
        ]
    )
    dimensions = conflicts.resolve(
        identifier,
        "dimensions",
        sourced_values(
            dimensions_values,
            "dimensions",
            cmor_transform=lambda value: [item.lower() for item in split_words(value)],
        ),
        default=[],
    )
    standard_observations = sourced_values(standard_names, "standard_name")
    if not any(not is_empty(value) for value, _, _ in standard_observations):
        standard_observations.append(
            (
                root_payload.get("standard_name"),
                f"resolved Variable/{root_name.lower()}",
                False,
            )
        )
    standard_name = conflicts.resolve(
        identifier,
        "cf_standard_name",
        standard_observations,
    )
    if standard_name is None:
        raise ValueError(f"No CF standard name found for {identifier!r}")
    known_units = conflicts.resolve(
        identifier,
        "units",
        sourced_values(units_values, "units"),
    )

    payload: dict[str, Any] = {
        "@context": "000_context.jsonld",
        "id": identifier,
        "type": "known_branded_variable",
        "drs_name": f"{root_payload['drs_name']}_{suffix}",
        "variable_root_name": root_name.lower(),
        "branding_suffix_name": suffix,
        "long_name": long_names or None,
        "cf_standard_name": standard_name,
        # out_name is the name CMOR writes to the data file. It commonly
        # matches the root DRS name, but historical/project definitions can
        # legitimately differ (for example legacy CMIP compound variables).
        "out_name": conflicts.resolve(
            identifier,
            "out_name",
            sourced_values((), "out_name"),
            default=root_payload["drs_name"],
        ),
        "units": known_units,
        "dimensions": dimensions,
        # References use lowercase vocabulary IDs. The mixed-case DRS forms are
        # retained in branding_suffix_name and on the resolved label terms.
        "temporal_label": temporal.lower(),
        "vertical_label": vertical.lower(),
        "horizontal_label": horizontal.lower(),
        "area_label": area.lower(),
        "var_def_qualifier": None,
        "history": KNOWN_BRANDED_VARIABLE_HISTORY,
        "bn_status": "accepted",
        "cf_sn_status": "approved",
        "table_id": unique(record.table_id.lower() for record in cmor_records),
        "compound_name": unique(compounds),
        "frequency": frequencies or None,
    }
    add_optional(payload, "comment", comments)
    add_optional(
        payload,
        "cell_methods",
        conflicts.resolve(
            identifier,
            "cell_methods",
            sourced_values(cell_methods_values, "cell_methods"),
        ),
    )
    add_optional(
        payload,
        "cell_measures",
        cell_measures_values,
    )
    add_optional(
        payload,
        "realm",
        realm_values,
    )

    flag_values = next(
        (
            parse_flag_values(record.entry.get("flag_values"))
            for record in cmor_records
            if not is_empty(record.entry.get("flag_values"))
        ),
        None,
    )
    flag_meanings = next(
        (
            split_words(record.entry.get("flag_meanings"))
            for record in cmor_records
            if not is_empty(record.entry.get("flag_meanings"))
        ),
        None,
    )
    if flag_values is not None:
        payload["flag_values"] = flag_values
    if flag_meanings is not None:
        payload["flag_meanings"] = flag_meanings
    return payload


def ensure_labels(
    known_payloads: dict[str, dict[str, Any]],
    universe_root: Path,
    *,
    dry_run: bool,
    report: dict[str, Any],
) -> None:
    definitions = (
        ("temporal_label", False),
        ("vertical_label", False),
        ("horizontal_label", False),
        ("area_label", True),
    )
    suffix_positions = {
        "temporal_label": 0,
        "vertical_label": 1,
        "horizontal_label": 2,
        "area_label": 3,
    }
    planned_paths: set[Path] = set()
    for payload in known_payloads.values():
        suffix_parts = str(payload["branding_suffix_name"]).split("-")
        suffix_drs_names = [
            suffix_parts[0],
            suffix_parts[1],
            suffix_parts[2],
            "-".join(suffix_parts[3:]),
        ]
        for field_name, is_area in definitions:
            label_id = str(payload[field_name]).lower()
            label_drs_name = suffix_drs_names[suffix_positions[field_name]]
            path = universe_root / field_name / f"{label_id}.json"
            if path.exists() or path in planned_paths:
                continue
            planned_paths.add(path)
            description = ""
            if field_name == "vertical_label":
                pressure = re.fullmatch(
                    r"(\d+)hpa", label_drs_name, flags=re.IGNORECASE
                )
                height = re.fullmatch(r"h(\d+)m", label_drs_name, flags=re.IGNORECASE)
                if pressure:
                    description = f"Data is reported at an atmospheric pressure of {pressure.group(1)} hPa."
                elif height:
                    description = (
                        f"Data is reported at a vertical height of {height.group(1)} m."
                    )
            label_payload: dict[str, Any] = {
                "@context": "000_context.jsonld",
                "id": label_id,
                "type": field_name,
                "description": description,
                "drs_name": label_drs_name,
            }
            if is_area:
                label_payload["cf_area_type"] = None
            emit(
                path,
                label_payload,
                dry_run=dry_run,
                report=report,
                category=f"universe_{field_name}",
            )
            report["warnings"].append(
                f"Created missing {field_name} {label_drs_name!r}; please review it manually"
            )


def main() -> None:
    args = parse_args()
    paths = resolve_paths(args)
    cmor_dir = paths["cmor"]
    universe_root = paths["universe"]
    project_root = paths["project"]
    if not cmor_dir.is_dir():
        raise FileNotFoundError(f"CMIP7 CMOR table directory not found: {cmor_dir}")
    report: dict[str, Any] = {
        "dry_run": args.dry_run,
        "dreq_version": args.dreq_version,
        "created_entries": {},
        "updated_entries": {},
        "overlay_differences": {},
        "warnings": [],
    }
    tables = load_dreq_tables(args.dreq_version, args.offline)
    cmor_variables = load_cmor_variables(cmor_dir)
    cmor_by_branded = cmor_records_by_branded_name(cmor_variables)
    dreq_by_branded = dreq_records_by_branded_name(tables["Variables"])
    missing_in_cmor = sorted(set(dreq_by_branded) - set(cmor_by_branded))
    missing_in_dreq = sorted(set(cmor_by_branded) - set(dreq_by_branded))
    if missing_in_cmor or missing_in_dreq:
        raise ValueError(
            "CMIP7 DReq and CMOR branded-variable sets differ: "
            f"DReq-only={missing_in_cmor}, CMOR-only={missing_in_dreq}"
        )

    # Resolve all Variable metadata before producing any CV output. The
    # conflict file itself and the report are the only files written when an
    # unresolved or changed conflict file stops the preflight.
    previous_conflict_payload = read_json_if_exists(args.conflicts_path)
    existing_conflict_defaults = load_existing_conflict_defaults(
        universe_root, project_root
    )
    conflicts = ConflictRegistry(
        previous_conflict_payload, existing_conflict_defaults
    )
    variable_payloads, root_ids = build_cmip7_variable_payloads(
        dreq_by_branded,
        tables,
        conflicts,
        report,
    )

    # Build known branded variables during the same read-only preflight so the
    # first run exposes all decisions, including project metadata conflicts.
    preflight_root_payloads = {
        root_id: preserve_existing_universe_payload(
            variable_payloads[root_id],
            read_json_if_exists(universe_root / "variable" / f"{root_id}.json"),
        )
        for root_id in root_ids
    }
    measure_path = cmor_dir / "CMIP7_cell_measures.json"
    cmor_cell_measures = (
        read_json(measure_path).get("cell_measures", {})
        if measure_path.exists()
        else {}
    )
    known_payloads = {
        identifier: build_known_payload(
            identifier,
            dreq_records,
            cmor_by_branded[identifier],
            preflight_root_payloads[split_branded_name(identifier)[0].lower()],
            tables,
            cmor_cell_measures,
            conflicts,
        )
        for identifier, dreq_records in sorted(dreq_by_branded.items())
    }
    conflict_payload = conflicts.payload()
    write_json(args.conflicts_path, conflict_payload)
    unresolved_conflicts = sorted(set(conflicts.unresolved))
    conflict_file_changed = previous_conflict_payload != conflict_payload
    review_required = conflict_file_requires_review(
        previous_conflict_payload, conflict_payload
    )
    report["cmip7_conflicts"] = {
        "path": str(args.conflicts_path),
        "counts_by_field": {
            field: len(terms) for field, terms in conflict_payload["conflicts"].items()
        },
        "unresolved": unresolved_conflicts,
        "file_changed": conflict_file_changed,
        "review_required": review_required,
    }
    if unresolved_conflicts or review_required:
        if unresolved_conflicts:
            reason = (
                f"{len(unresolved_conflicts)} metadata conflict(s) require a selection"
            )
        else:
            reason = "the conflict file changed and requires review"
        report["warnings"].append(
            f"CMIP7 generation stopped before CV writes: {reason}"
        )
        write_json(args.report_path, report)
        if unresolved_conflicts:
            print(
                f"Unresolved CMIP7 metadata conflicts: {len(unresolved_conflicts)}. "
                f"Edit {args.conflicts_path} so exactly one candidate has use=1 "
                "for each conflict, then rerun."
            )
        else:
            print(
                f"CMIP7 conflict selections were updated in {args.conflicts_path}. "
                "Review the selected use=1 candidates, then rerun. An unchanged, "
                "fully resolved conflict file will be applied directly."
            )
        raise SystemExit(2)

    generate_contexts(
        universe_root,
        project_root,
        dry_run=args.dry_run,
        report=report,
    )

    for identifier, description in COORDINATE_TYPES.items():
        candidate = {
            "@context": "000_context.jsonld",
            "id": identifier,
            "type": "coordinate_type",
            "description": description,
            "drs_name": identifier,
        }
        path = universe_root / "coordinate_type" / f"{identifier}.json"
        payload = preserve_existing_universe_payload(
            candidate, read_json_if_exists(path)
        )
        if not path.exists():
            validate_payload("coordinate_type", payload)
        emit(
            path,
            payload,
            dry_run=args.dry_run,
            report=report,
            category="universe_coordinate_type",
        )

    existing_variable_differences: dict[str, dict[str, Any]] = {}
    for variable_id, full_payload in sorted(variable_payloads.items()):
        universe_path = universe_root / "variable" / f"{variable_id}.json"
        existing_universe = read_json_if_exists(universe_path)
        universe_payload = preserve_existing_universe_payload(
            full_payload, existing_universe
        )
        if existing_universe is None:
            validate_payload("variable", universe_payload)
        else:
            _, universe_differences = project_overlay(full_payload, universe_payload)
            if universe_differences:
                existing_variable_differences[variable_id] = universe_differences
        emit(
            universe_path,
            universe_payload,
            dry_run=args.dry_run,
            report=report,
            category="universe_variable",
        )
        # Physical-parameter-only Variable terms are shared Universe concepts.
        # The CMIP7 project Variable collection continues to contain the
        # branded-variable roots used by its existing CV layout.
        if variable_id not in root_ids:
            continue
        overlay, differences = project_overlay(full_payload, universe_payload)
        report["overlay_differences"].setdefault("variable", {})[variable_id] = (
            differences
        )
        emit(
            project_root / "variable" / f"{variable_id}.json",
            overlay,
            dry_run=args.dry_run,
            report=report,
            category="project_variable",
        )
    report["existing_universe_variable_differences"] = existing_variable_differences

    dreq_coordinates = merge_dreq_coordinate_records(
        tables["Coordinates and Dimensions"], report
    )
    coordinate_content = read_json(cmor_dir / "CMIP7_coordinate.json")
    cmor_coordinates = coordinate_content.get("axis_entry", {})
    formula_content = read_json(cmor_dir / "CMIP7_formula_terms.json")
    formula_entries = formula_content.get("formula_entry", {})
    formula_term_ids = {identifier.lower() for identifier in formula_entries}
    model_level_entries = {
        identifier: entry
        for identifier, entry in cmor_coordinates.items()
        if not is_empty(entry.get("generic_level_name"))
    }
    data_coordinate_ids = (set(dreq_coordinates) | set(cmor_coordinates)) - set(
        model_level_entries
    )
    data_payloads = {
        identifier: build_data_coordinate_payload(
            identifier,
            dreq_coordinates.get(identifier),
            cmor_coordinates.get(identifier),
        )
        for identifier in sorted(data_coordinate_ids)
    }
    for identifier in GENERIC_LEVEL_METADATA:
        data_payloads[identifier] = build_generic_coordinate_payload(
            identifier, dreq_coordinates.get(identifier)
        )
    data_payloads["vertices"] = build_vertices_coordinate_payload()
    for payload in data_payloads.values():
        emit_layered_payload(
            "data_coordinate",
            payload,
            universe_root,
            project_root,
            dry_run=args.dry_run,
            report=report,
        )

    for identifier, entry in sorted(model_level_entries.items()):
        emit_layered_payload(
            "model_level_coordinate",
            build_model_level_payload(identifier, entry, formula_term_ids),
            universe_root,
            project_root,
            dry_run=args.dry_run,
            report=report,
        )

    for identifier, entry in sorted(formula_entries.items()):
        emit_layered_payload(
            "formula_term",
            build_formula_term_payload(identifier, entry),
            universe_root,
            project_root,
            dry_run=args.dry_run,
            report=report,
        )

    grid_content = read_json(cmor_dir / "CMIP7_grids.json")
    for identifier, entry in sorted(grid_content.get("axis_entry", {}).items()):
        emit_layered_payload(
            "grid_axis",
            build_grid_axis_payload(identifier, entry),
            universe_root,
            project_root,
            dry_run=args.dry_run,
            report=report,
        )
    for identifier, entry in sorted(grid_content.get("variable_entry", {}).items()):
        emit_layered_payload(
            "grid_variable",
            build_grid_variable_payload(identifier, entry),
            universe_root,
            project_root,
            dry_run=args.dry_run,
            report=report,
        )

    for table_id, project_table in sorted(load_table_payloads(cmor_dir).items()):
        universe_path = universe_root / "table" / f"{table_id.lower()}.json"
        existing_universe = read_json_if_exists(universe_path)
        universe_table = preserve_existing_universe_payload(
            {
                "@context": "000_context.jsonld",
                "id": table_id.lower(),
                "type": "table",
                "description": f"Table identifier used by CMIP7 {table_id}.",
                "drs_name": table_id,
                "product": None,
                "table_date": None,
                "variable_entry": [],
            },
            existing_universe,
        )
        if existing_universe is None:
            validate_payload("table", universe_table)
        emit(
            universe_path,
            universe_table,
            dry_run=args.dry_run,
            report=report,
            category="universe_table",
        )
        overlay, differences = project_overlay(project_table, universe_table)
        report["overlay_differences"].setdefault("table", {})[table_id] = differences
        emit(
            project_root / "table" / f"{table_id.lower()}.json",
            overlay,
            dry_run=args.dry_run,
            report=report,
            category="project_table",
        )

    for payload in known_payloads.values():
        emit_layered_payload(
            "known_branded_variable",
            payload,
            universe_root,
            project_root,
            dry_run=args.dry_run,
            report=report,
        )
    ensure_labels(
        known_payloads,
        universe_root,
        dry_run=args.dry_run,
        report=report,
    )
    write_json(args.report_path, report)
    print("#" * 60)
    print(f"DReq release: {args.dreq_version}")
    print(f"CMOR variable records processed: {len(cmor_variables)}")
    print(f"Unique variable roots: {len(root_ids)}")
    print(f"Unique Variable terms (root/physical union): {len(variable_payloads)}")
    print(f"Metadata conflict file: {args.conflicts_path}")
    print(f"Unique known branded variables: {len(known_payloads)}")
    print(f"Data coordinates: {len(data_payloads)}")
    print(f"Model-level coordinates: {len(model_level_entries)}")
    print(f"Run mode: {'dry-run' if args.dry_run else 'write'}")
    print(f"Warnings: {len(report['warnings'])}")
    print(f"Report: {args.report_path}")


if __name__ == "__main__":
    main()
