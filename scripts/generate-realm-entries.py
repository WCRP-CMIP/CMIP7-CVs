"""
Generate realm entries
"""

import json


def main():
    to_write = [
        "aerosol",
        "atmos",
        "atmosChem",
        "land",
        "landIce",
        "ocean",
        "ocnBgchem",
        "seaIce",
    ]

    for drs_name in to_write:
        id = drs_name.lower()
        content = {
            "@context": "000_context.jsonld",
            "id": id,
            "type": "realm",
        }

        out_file = f"realm/{id}.json"
        with open(out_file, "w") as fh:
            json.dump(content, fh, indent=4)
            fh.write("\n")

        print(f"Wrote {out_file}")


if __name__ == "__main__":
    main()
