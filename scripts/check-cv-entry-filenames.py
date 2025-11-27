"""
Check that all entries' filename matches their ID
"""

import json
import os
from pathlib import Path


def main():
    REPO_ROOT = Path(__file__).parents[1]

    failing = []
    for cvs_folder in (f.path for f in os.scandir(REPO_ROOT) if f.is_dir()):
        if cvs_folder.endswith("scripts"):
            continue

        for cv_file in Path(cvs_folder).glob("*.json"):
            with open(cv_file) as fh:
                content = json.load(fh)

            if cv_file.stem != content["id"]:
                failing.append(f"{content['id']}: {cv_file}")

    if failing:
        raise AssertionError(failing)


if __name__ == "__main__":
    main()
