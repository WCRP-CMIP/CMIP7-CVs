"""
Generate nominal resolution entries
"""

import json
from pathlib import Path


def main():
    repo_root = Path(__file__).parents[1]
    include_from = repo_root / ".." / "WCRP-universe" / "nominal_resolution"

    for src_file in include_from.glob("*.json"):
        id = src_file.stem.lower()
        content = {
            "@context": "000_context.jsonld",
            "id": id,
            "type": "nominal_resolution",
        }

        out_file = f"nominal_resolution/{id}.json"
        with open(out_file, "w") as fh:
            json.dump(content, fh, indent=4)
            fh.write("\n")

        print(f"Wrote {out_file}")


if __name__ == "__main__":
    main()
