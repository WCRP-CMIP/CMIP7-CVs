"""Utilities for reading GitHub issue form Markdown bodies."""

from __future__ import annotations

import re

NO_RESPONSE_VALUES = {"", "_No response_", "No response"}


def parse_issue_form_body(body: str) -> dict[str, str]:
    """Parse a GitHub issue form body into a mapping from heading to value.

    >>> body = '''
    ... ### Experiment name
    ...
    ... My-Experiment
    ...
    ... ### Parent experiment
    ...
    ... _No response_
    ... '''
    >>> parse_issue_form_body(body)
    {'Experiment name': 'My-Experiment', 'Parent experiment': ''}
    """
    heading_pattern = re.compile(r"^### (?P<label>.+?)\s*$", re.MULTILINE)
    matches = list(heading_pattern.finditer(body or ""))
    fields: dict[str, str] = {}

    for index, match in enumerate(matches):
        label = match.group("label").strip()
        start = match.end()
        end = matches[index + 1].start() if index + 1 < len(matches) else len(body)
        value = body[start:end].strip()
        if value in NO_RESPONSE_VALUES:
            value = ""
        fields[label] = value

    return fields
