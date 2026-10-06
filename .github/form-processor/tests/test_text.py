import json

import pytest

from github_form_processor.text import dumps_json, to_plain_text


@pytest.mark.parametrize(
    "value, expected",
    (
        ("fire\u2019s role", "fire's role"),
        ("\u2018single\u2019 \u201cdouble\u201d", "'single' \"double\""),
        ("1850\u20131900 \u2014 pre-industrial", "1850-1900 - pre-industrial"),
        ("non\u00a0breaking\u202fspaces", "non breaking spaces"),
        ("zero\u200bwidth", "zerowidth"),
        ("plain `ascii` stays", "plain `ascii` stays"),
        # Letters in names are kept (and composed)
        ("M\u00e9t\u00e9o-France", "M\u00e9t\u00e9o-France"),
        ("Me\u0301te\u0301o-France", "M\u00e9t\u00e9o-France"),
    ),
)
def test_to_plain_text(value, expected):
    assert to_plain_text(value) == expected


def test_dumps_json_has_no_unicode_escapes():
    payload = {
        "description": "fire\u2019s \u201crole\u201d",
        "labels": ["M\u00e9t\u00e9o-France"],
        "tier": 1,
        "parent": None,
    }
    # Sanity check of the failure mode we're avoiding
    assert "\\u2019" in json.dumps(payload)

    res = dumps_json(payload)

    assert "\\u" not in res
    assert json.loads(res) == {
        "description": 'fire\'s "role"',
        "labels": ["M\u00e9t\u00e9o-France"],
        "tier": 1,
        "parent": None,
    }
