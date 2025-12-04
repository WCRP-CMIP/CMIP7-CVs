"""
Export hydrated CVs to excel

Uses the environment created with `create-cmor-cvs-table-export-environment.sh`
"""

from pathlib import Path
from typing import Any

import esgvoc.api as ev
import pandas as pd


def extract_id_if_needed(v: Any) -> Any:
    if isinstance(v, dict) and "id" in v:
        return v["id"]

    if isinstance(v, list):
        return [extract_id_if_needed(vv) for vv in v]

    return v


def main():
    out_file = "cvs-export.xlsx"
    out_dir_csvs = Path("cvs-as-csvs")
    out_dir_csvs.mkdir(exist_ok=True, parents=True)

    with pd.ExcelWriter(out_file, engine="openpyxl", mode="w") as writer:
        # All required global attributes
        for collection in [
            "activity",
            "archive",
            "area_label",
            "branded_suffix",
            "branded_variable",
            "institution",
            "conventions",
            "creation_date",
            "data_specs_version",
            "directory_date",
            "drs_specs",
            "experiment",
            "forcing_index",
            "frequency",
            "grid",
            "horizontal_label",
            "initialization_index",
            "license",
            "mip_era",
            "nominal_resolution",
            "organisation",
            "physics_index",
            "product",
            "realization_index",
            "realm",
            "region",
            "source",
            "temporal_label",
            "time_range",
            "tracking_id",
            "variable",
            "variant_label",
            "vertical_label",
        ]:
            ev_obj = ev.get_all_terms_in_collection("cmip7", collection)
            if not ev_obj:
                msg = f"{collection=} is empty"
                raise ValueError(msg)

            df_l = []
            for item in ev_obj:
                tmp = item.model_dump(mode="json")
                for k in tmp:
                    tmp[k] = extract_id_if_needed(tmp[k])

                df_l.append(tmp)

            df = pd.DataFrame(df_l).sort_values("id").reset_index(drop=True)

            # workbook = writer.book
            sheet_name = collection
            df.to_excel(
                writer,
                sheet_name=sheet_name,
                startrow=0,
                index=True,
            )

            csv_file = out_dir_csvs / f"{collection.replace(' ', '_')}.csv"
            df.to_csv(csv_file)
            print(f"Wrote {csv_file}")

    print(f"Wrote {out_file}")


if __name__ == "__main__":
    main()
