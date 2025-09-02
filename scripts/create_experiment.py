import json
import os
from pathlib import Path
from datetime import datetime

import esgvoc.api as ev
import requests

# URLs of the JSON files on GitHub
json_url = "https://raw.githubusercontent.com/WCRP-CMIP/CMIP7-CVs/refs/heads/main/CMIP7-CVs_experiment.json"

# Directory where the JSON files will be saved
save_dir = "CMIP7_experiment"

# Create the directory if it doesn't exist
os.makedirs(save_dir, exist_ok=True)


# Function to fetch and load JSON data from a URL
def fetch_json(url):
    response = requests.get(url)
    response.raise_for_status()  # Check for request errors
    return response.json()


def get_parent_activity_id(value: str, experiment_dir: str = "experiment"):
    if value == "none":
        return [None]

    project_root = Path.cwd().parent
    experiment_dir = project_root / "WCRP-universe" / "experiment"
    parent_file = os.path.join(experiment_dir, f"{value}.json")

    if not os.path.exists(parent_file):
        print(f"Parent file for {value} not found : {parent_file}")
        return [None]

    with open(parent_file, "r", encoding="utf-8") as f:
        parent_data = json.load(f)

    return parent_data.get("activity_id")


def normalize_experiment_data(experiment_data):
    print(experiment_data)
    start_year = experiment_data.get('start-date', experiment_data.get('start_year', ''))
    end_year = experiment_data.get('end', experiment_data.get('end_year', ''))

    if not isinstance(start_year, int):
        try:
            if start_year.lower() != "none":
                start_year = datetime.fromisoformat(start_year).year
        except ValueError:
            start_year = None
    try:
        end_year = int(end_year)
    except ValueError:
        end_year = None  # or handle as needed if conversion fails
    
    model_realms = experiment_data.get('model-realms', [])
    if isinstance(model_realms, dict):
        model_realms = [model_realms]

    return {
        'activity_id': experiment_data.get('activity', []),
        'additional_allowed_model_components': model_realms,
        'description': experiment_data.get('description', ''),
        'end_year':end_year,
        'experiment': experiment_data.get('ui-label', ''),
        'experiment_id': experiment_data.get('validation-key', ''),
        'min_number_yrs_per_sim': experiment_data.get('minimum-number-of-years') if (experiment_data.get('minimum-number-of-years') != "none" and experiment_data.get('minimum-number-of-years') != "") else None,
        'parent_experiment_id': experiment_data.get('parent-experiment', []),
        'start_year': start_year,
        'sub_experiment_id': experiment_data.get('sub_experiment_id', []),
        'tier': experiment_data.get('tier', '')
    }


data = fetch_json(json_url)["experiment"]

known_sources_in_universe = ev.get_all_terms_in_data_descriptor("experiment")
# print(known_sources_in_universe)
for item, content in data.items():
    found_item = None
    for experiment in known_sources_in_universe:
        if experiment.drs_name == item:
            found_item = experiment
            break

    if found_item is None:
        print(item, "not found in universe")
    else:
        normalized_data = normalize_experiment_data(content)
        # Create json file
        dict_to_save = {
            "@context": "000_context.jsonld",
            "id": found_item.id,
            "type": found_item.type,
            "additional_allowed_model_components": [v.get('id').split('/')[-1].lower() for v in normalized_data['additional_allowed_model_components']],
            "description": normalized_data["description"],
            "end_year": int(normalized_data['start_year']) + int(normalized_data['min_number_yrs_per_sim']) - 1 if (normalized_data['start_year'] and normalized_data['min_number_yrs_per_sim'] and normalized_data['start_year'] != "none") else normalized_data['end_year'],
            "experiment": normalized_data['experiment'],
            "min_number_yrs_per_sim": normalized_data['min_number_yrs_per_sim'] if (normalized_data['min_number_yrs_per_sim'] != "none" and normalized_data['min_number_yrs_per_sim']!="" ) else None,
            'parent_activity_id': get_parent_activity_id(normalized_data['parent_experiment_id'].split('/')[-1].lower()),
            'parent_experiment_id': [normalized_data['parent_experiment_id'].split('/')[-1].lower() if normalized_data['parent_experiment_id'].split('/')[-1].lower() != "none" else None],
            'required_model_components': [v.get('id').split('/')[-1].lower() for v in normalized_data['additional_allowed_model_components'] if v.get("is-required")],
            "tier": normalized_data["tier"]
        }
        # print(dict_to_save)
        with open(Path(save_dir) / f"{found_item.id}.json", "w") as f:
            json.dump(dict_to_save, f, indent=4)
