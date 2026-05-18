"""
Generate ScenarioMIP experiment names
"""

import json


def get_tier(experiment: str) -> int:
    # TODO: confirm this
    return 0


def main():
    bases = [
        ("vl", "PLACEHOLDER TBC. CMIP7 ScenarioMIP Very low emissions future."),
        (
            "ln",
            "PLACEHOLDER TBC. CMIP7 ScenarioMIP Low followed by negative (steep reductions begin in 2040, negative from TBD) emissions future.",
        ),
        ("l", "PLACEHOLDER TBC. CMIP7 ScenarioMIP Low emissions future."),
        (
            "ml",
            "PLACEHOLDER TBC. CMIP7 ScenarioMIP Medium followed by low (from 2040) emissions future.",
        ),
        ("m", "PLACEHOLDER TBC. CMIP7 ScenarioMIP Medium emissions future."),
        (
            "hl",
            "PLACEHOLDER TBC. CMIP7 ScenarioMIP High followed by low (from 2060) emissions future.",
        ),
        ("h", "PLACEHOLDER TBC. CMIP7 ScenarioMIP High emissions future."),
    ]

    for base, base_description in bases:
        for prefix, run_mode_description, no_suffix_parent_experiment in [
            (
                "scen7-",
                "Run with prescribed concentrations of CO2 (for runs with prescribed emissions of CO2, see the `esm-scen7-` experiments).",
                "historical",
            ),
            (
                "esm-scen7-",
                "Run with prescribed emissions of CO2 (for runs with prescribed concentrations of CO2, see the `scen7-` experiments).",
                "esm-hist",
            ),
        ]:
            experiment_name_excl_suffix = f"{prefix}{base}"
            for (
                suffix,
                suffix_description,
                start_timestamp,
                end_timestamp,
                min_number_yrs_per_sim,
                parent_experiment,
                parent_activity,
            ) in [
                # TODO: check start and end timestamps and min_number_yrs_per_sim
                (
                    "",
                    None,
                    "2022-01-01",
                    "2100-01-01",
                    78,
                    no_suffix_parent_experiment,
                    "cmip",
                ),
                (
                    "-ext",
                    "Extension beyond 2100",
                    "2100-01-01",
                    "2300-01-01",
                    51,
                    experiment_name_excl_suffix,
                    "scenariomip",
                ),
            ]:
                if suffix:
                    experiment_name = f"{experiment_name_excl_suffix}{suffix}"
                else:
                    experiment_name = experiment_name_excl_suffix

                tier = get_tier(experiment_name)

                description = f"{base_description} {run_mode_description}"
                if suffix_description:
                    description = f"{description} {suffix_description}"

                branch_information = (
                    f"Branch from {parent_experiment} at {start_timestamp}."
                )

                id = experiment_name.lower()

                content = {
                    "@context": "000_context.jsonld",
                    "id": id,
                    "type": "experiment",
                    "description": description,
                    "branch_information": branch_information,
                    "end_timestamp": end_timestamp,
                    "min_ensemble_size": 1,
                    "min_number_yrs_per_sim": min_number_yrs_per_sim,
                    "parent_activity": parent_activity,
                    "parent_experiment": parent_experiment,
                    "parent_mip_era": "cmip7",
                    "start_timestamp": start_timestamp,
                    "tier": tier,
                }

                out_file = f"experiment/{id}.json"
                with open(out_file, "w") as fh:
                    json.dump(content, fh, indent=4)

                print(f"Wrote {out_file}")


if __name__ == "__main__":
    main()
