"""
Check that all entries are ASCII, with non-ASCII characters encoded as LaTeX

Every string (keys included) must be unchanged by
`github_form_processor.text.to_ascii_latex`, i.e.:

- typographic characters (curly quotes, dashes, special spaces etc.)
  must already be replaced by their plain ASCII equivalents
- all other non-ASCII characters (e.g. accented letters)
  must already be encoded as LaTeX (e.g. `\\'e`)

Characters written as JSON escapes (e.g. `\\u00e9`) are treated the same
as the characters themselves, because they end up in the loaded values
in exactly the same way.

The only exceptions are the specific values in `EXEMPTIONS`,
which may contain characters that have no LaTeX equivalent.

This needs the form processor to be installed, e.g. run it with

```
.github/form-processor/.venv/bin/python scripts/check-cv-entries-are-ascii.py
```
"""

import json
import logging
import os
from collections.abc import Iterator
from pathlib import Path
from typing import Any

from github_form_processor.text import to_ascii_latex

# Values which are allowed to contain non-ASCII characters,
# keyed by the path to the entry (relative to the root of the repository).
# Only for values that can't be written in ASCII, even with LaTeX
# (e.g. names in their native script).
EXEMPTIONS: dict[str, tuple[str, ...]] = {}


def get_strings(value: Any) -> Iterator[str]:
    """Get all the strings in a loaded JSON value (keys included)"""
    if isinstance(value, str):
        yield value

    elif isinstance(value, list):
        for v in value:
            yield from get_strings(v)

    elif isinstance(value, dict):
        for k, v in value.items():
            yield k
            yield from get_strings(v)


def as_json(value: str) -> str:
    """Show a value as it should be written in the JSON file"""
    return json.dumps(value, ensure_ascii=False)


def main():
    # We report characters with no LaTeX equivalent ourselves
    logging.getLogger("pylatexenc").setLevel(logging.ERROR)

    REPO_ROOT = Path(__file__).parents[1]

    failing = []
    used_exemptions = set()
    for cvs_folder in (f.path for f in os.scandir(REPO_ROOT) if f.is_dir()):
        if cvs_folder.endswith("scripts") or cvs_folder.endswith(".venv"):
            continue

        for cv_file in sorted(Path(cvs_folder).glob("*.json")):
            cv_file_rel = cv_file.relative_to(REPO_ROOT).as_posix()
            with open(cv_file, encoding="utf-8") as fh:
                content = json.load(fh)

            for value in get_strings(content):
                expected = to_ascii_latex(value)
                if value != expected:
                    failing.append(
                        f"{cv_file_rel}: {as_json(value)} should be {as_json(expected)}"
                    )
                    continue

                if value.isascii():
                    continue

                if value in EXEMPTIONS.get(cv_file_rel, ()):
                    used_exemptions.add((cv_file_rel, value))
                    continue

                non_ascii = ", ".join(
                    f"{c!r} (U+{ord(c):04X})"
                    for c in sorted({c for c in value if not c.isascii()})
                )
                failing.append(
                    f"{cv_file_rel}: {as_json(value)} contains {non_ascii}, "
                    "which have no LaTeX equivalent. "
                    "If this is e.g. a name in its native script, "
                    "add it to `EXEMPTIONS` in this script."
                )

    for cv_file_rel, values in EXEMPTIONS.items():
        for value in values:
            if (cv_file_rel, value) not in used_exemptions:
                failing.append(
                    f"Unused exemption, please remove it: {cv_file_rel}: {value!r}"
                )

    if failing:
        raise AssertionError("\n".join(failing))


if __name__ == "__main__":
    main()
