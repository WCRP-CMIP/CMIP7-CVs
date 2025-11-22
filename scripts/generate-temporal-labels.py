"""
Generate temporal label entries
"""

import json


def main():
    to_write = [
        "tmax",
        "tmin",
        "tsum",
        "tavg",
        "tpt",
        "tclm",
        "tclmdc",
        "tmaxavg",
        "tminavg",
        "ti",
    ]

    for drs_name in to_write:
        id = drs_name.lower()
        content = {
            "@context": "000_context.jsonld",
            "id": id,
            "type": "temporal_label",
        }

        out_file = f"temporal_label/{id}.json"
        with open(out_file, "w") as fh:
            json.dump(content, fh, indent=4)
            fh.write("\n")

        print(f"Wrote {out_file}")


if __name__ == "__main__":
    main()
