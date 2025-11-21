"""
Generate region entries
"""

import json


def main():
    to_write = [
        "glb",
        "ata",
        "grl",
        "30S-90S",
        "nh",
        "sh",
    ]

    for drs_name in to_write:
        id = drs_name.lower()
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
