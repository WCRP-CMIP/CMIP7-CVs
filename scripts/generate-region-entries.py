"""
Generate region entries
"""

import json


def main():
    to_write = [
        ("glb", "global"),
        ("ata", "antarctica"),
        ("grl", "greenland"),
        ("30S-90S", "30s-90s"),
        ("nh", "northern-hemisphere"),
        ("sh", "southern-hemisphere"),
    ]

    for drs_name, id in to_write:
        content = {
            "@context": "000_context.jsonld",
            "id": id,
            "type": "region",
        }

        out_file = f"region/{id}.json"
        with open(out_file, "w") as fh:
            json.dump(content, fh, indent=4)
            fh.write("\n")

        print(f"Wrote {out_file}")


if __name__ == "__main__":
    main()
