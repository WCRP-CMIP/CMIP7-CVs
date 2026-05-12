"""Render registration models to CV-style JSON files."""

from __future__ import annotations

import json
from typing import Any

from github_form_processor.models import ActivityRegistration, ExperimentRegistration


def render_experiment_json(experiment: ExperimentRegistration) -> str:
    """Render an experiment registration as a JSON file."""
    payload: dict[str, Any] = {
        "@context": "000_context.jsonld",
        "id": experiment.identifier,
        "type": "experiment",
        "description": experiment.description,
        "drs_name": experiment.name,
        "start_timestamp": experiment.start_date.isoformat()
        if experiment.start_date
        else None,
        "end_timestamp": experiment.end_date.isoformat()
        if experiment.end_date
        else None,
        "activity": experiment.activity,
        "additional_allowed_model_components": (
            experiment.additional_allowed_model_components
        ),
        "branch_information": experiment.branch_information,
        "min_ensemble_size": experiment.min_ensemble_size,
        "parent_activity": experiment.parent_activity,
        "parent_experiment": experiment.parent_experiment,
        "parent_mip_era": experiment.parent_mip_era,
        "required_model_components": experiment.required_model_components,
        "tier": experiment.tier,
        "min_number_yrs_per_sim": experiment.min_number_yrs_per_sim,
    }
    return json.dumps(payload, indent=4) + "\n"


def render_activity_json(activity: ActivityRegistration) -> str:
    """Render an activity registration as a JSON file."""
    payload: dict[str, Any] = {
        "@context": "000_context.jsonld",
        "id": activity.identifier,
        "type": "activity",
        "description": activity.description,
        "drs_name": activity.name,
        "experiments": activity.experiments,
        "urls": activity.urls,
    }
    return json.dumps(payload, indent=4) + "\n"
