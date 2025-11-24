"""
Generate area label entries
"""

import json


def main():
    to_write = [
        "air",
        "cl",
        "ccl",
        "crp",
        "fis",
        "gis",
        "ifs",
        "is",
        "lnd",
        "li",
        "ng",
        "pst",
        "sea",
        "si",
        "simp",
        "sir",
        "multilus",
        "shb",
        "sn",
        "scl",
        "tree",
        "ufs",
        "veg",
        "wl",
        "lsi",
        "u",
    ]

    for drs_name in to_write:
        id = drs_name.lower()
        content = {
            "@context": "000_context.jsonld",
            "id": id,
            "type": "area_label",
        }

        out_file = f"area_label/{id}.json"
        with open(out_file, "w") as fh:
            json.dump(content, fh, indent=4)
            fh.write("\n")

        print(f"Wrote {out_file}")


if __name__ == "__main__":
    main()
