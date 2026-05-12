"""Tests for issue form body parsing."""

from github_form_processor.issue_body import parse_issue_form_body


def test_parse_issue_form_body_extracts_headings_and_values():
    body = """
### Experiment name

My-Experiment

### Parent experiment

_No response_
"""

    fields = parse_issue_form_body(body)

    assert fields == {
        "Experiment name": "My-Experiment",
        "Parent experiment": "",
    }
