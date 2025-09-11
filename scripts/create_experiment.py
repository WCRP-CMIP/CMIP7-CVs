import json
import os
from pathlib import Path
from datetime import datetime

import esgvoc.api as ev
import requests
from icecream import IceCreamDebugger
import devtools

ic = IceCreamDebugger(argToStringFunction=devtools.pformat)

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


def transform_json_to_model(json_data: dict) -> dict:
    """Transform the input JSON to match your existing Pydantic model structure"""

    # Extract activity from the activity field
    activity = []
    if "activity" in json_data and json_data["activity"]:
        activity_id = (
            json_data["activity"].split("/")[-1]
            if "/" in json_data["activity"]
            else json_data["activity"]
        )
        activity.append(activity_id)

    # Extract required and additional model components
    model_realms = json_data.get("model-realms", [])
    required_components = []
    additional_components = []
    if isinstance(model_realms, list):
        for realm in model_realms:
            component = (
                realm["id"].split("/")[-1] if "/" in realm["id"] else realm["id"]
            )
            if realm.get("is-required", False):
                required_components.append(component)
            else:
                additional_components.append(component)
    else:
        component = (
            model_realms["id"].split("/")[-1]
            if "/" in model_realms["id"]
            else model_realms["id"]
        )
        if model_realms.get("is-required", False):
            required_components.append(component)
        else:
            additional_components.append(component)

    # Extract parent experiment
    parent_exp = json_data.get("parent-experiment", "none")
    parent_experiment_id = (
        ["no parent"]
        if parent_exp == "cmip7:experiment/none" or parent_exp == "none"
        else [parent_exp.split("/")[-1]]
    )

    # Convert minimum years
    min_years = json_data.get("minimum-number-of-years")
    if isinstance(min_years, str) and min_years.isdigit():
        min_years = int(min_years)
    elif min_years == "none" or not min_years:
        min_years = None

    return {
        "id": json_data.get("validation-key", "").lower(),
        "type": "experiment",
        "drs_name": json_data.get("validation-key", ""),
        "activity": activity,
        "description": json_data.get("description", ""),
        "tier": int(json_data.get("tier")),
        "experiment_id": json_data.get("validation-key", "").lower(),
        "sub_experiment_id": ["none"],  # Default as shown in your example
        "experiment": json_data.get("ui-label", ""),
        "required_model_components": required_components,
        "additional_allowed_model_components": additional_components,
        "start_year": None
        if json_data.get("start-date") == "none"
        else json_data.get("start-date"),
        "end_year": None
        if json_data.get("end-date") == "none"
        else json_data.get("end-date"),
        "min_number_yrs_per_sim": min_years,
        # "parent_activity_id": ["no parent"],  # Doesnot exist in CMIP7
        "parent_experiment_id": parent_experiment_id,
        "@context": "000_context.jsonld",
        "activity_id": activity,
    }


def compare_models(model1_dict: dict, model2_dict: dict) -> dict:
    """Compare two model dictionaries and return differences"""

    differences = {
        "only_in_model1": {},
        "only_in_model2": {},
        "different_values": {},
        "same_values": {},
    }

    all_keys = set(model1_dict.keys()) | set(model2_dict.keys())

    for key in all_keys:
        if key not in model1_dict:
            differences["only_in_model2"][key] = model2_dict[key]
        elif key not in model2_dict:
            differences["only_in_model1"][key] = model1_dict[key]
        elif model1_dict[key] != model2_dict[key]:
            differences["different_values"][key] = {
                "model1": model1_dict[key],
                "model2": model2_dict[key],
            }
        else:
            differences["same_values"][key] = model1_dict[key]

    return differences


#
# def get_parent_activity_id(value: str, experiment_dir: str = "experiment"):
#     if value == "none":
#         return ["no parent"]
#
#     project_root = Path.cwd().parent
#     experiment_dir = project_root / "WCRP-universe" / "experiment"
#     parent_file = os.path.join(experiment_dir, f"{value}.json")
#
#     if not os.path.exists(parent_file):
#         print(f"Parent file for {value} not found : {parent_file}")
#         return ["no parent"]
#
#     with open(parent_file, "r", encoding="utf-8") as f:
#         parent_data = json.load(f)
#
#     return parent_data.get("activity_id")
#
#
# def normalize_experiment_data(experiment_data):
#     print(experiment_data)
#     start_year = experiment_data.get(
#         "start-date", experiment_data.get("start_year", "")
#     )
#     end_year = experiment_data.get("end", experiment_data.get("end_year", ""))
#
#     if not isinstance(start_year, int):
#         try:
#             if start_year.lower() != "none":
#                 start_year = datetime.fromisoformat(start_year).year
#         except ValueError:
#             start_year = None
#     try:
#         end_year = int(end_year)
#     except ValueError:
#         end_year = None  # or handle as needed if conversion fails
#
#     model_realms = experiment_data.get("model-realms", [])
#     if isinstance(model_realms, dict):
#         model_realms = [model_realms]
#
#     return {
#         "activity_id": experiment_data.get("activity", []),
#         "additional_allowed_model_components": model_realms,
#         "description": experiment_data.get("description", ""),
#         "end_year": end_year,
#         "experiment": experiment_data.get("ui-label", ""),
#         "experiment_id": experiment_data.get("validation-key", ""),
#         "min_number_yrs_per_sim": experiment_data.get("minimum-number-of-years")
#         if (
#             experiment_data.get("minimum-number-of-years") != "none"
#             and experiment_data.get("minimum-number-of-years") != ""
#         )
#         else None,
#         "parent_experiment_id": experiment_data.get("parent-experiment", []),
#         "start_year": start_year,
#         "sub_experiment_id": experiment_data.get("sub_experiment_id", []),
#         "tier": experiment_data.get("tier", ""),
#     }
#

data = fetch_json(json_url)["experiment"]

known_experiment_in_universe = ev.get_all_terms_in_data_descriptor("experiment")
# ic(known_experiment_in_universe)
for item, content in data.items():
    found_item = None
    for experiment in known_experiment_in_universe:
        if experiment.drs_name == item:
            found_item = experiment
            break

    if found_item is None:
        print(item, "not found in universe")
    else:
        ic(found_item)
        term_from_json = transform_json_to_model(content)
        ic(term_from_json)
        term_in_universe = ev.get_term_in_data_descriptor(
            "experiment", found_item.id
        ).dict()

        ic(term_in_universe)
        compare = compare_models(term_from_json, term_in_universe)
        ic(compare)
        # normalized_data = normalize_experiment_data(content)
        # ic(normalized_data)
        # Create json file
        dict_to_save = {
            "@context": "000_context.jsonld",
            "id": found_item.id,
            "type": found_item.type,
        }
        overload_dict = {
            k: v["model1"] for k, v in compare["different_values"].items()
        }  # dict_to_save = (
        dict_to_save = dict_to_save | overload_dict
        # print(dict_to_save)
        with open(Path(save_dir) / f"{found_item.id}.json", "w") as f:
            json.dump(dict_to_save, f, indent=4)
