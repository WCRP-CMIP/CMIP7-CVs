import json

import pytest

from github_form_processor.text import dumps_json, to_ascii_latex, to_plain_text


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


@pytest.mark.parametrize(
    "value, expected",
    (
        # Typography goes to plain ASCII
        ("fire\u2019s \u201crole\u201d", 'fire\'s "role"'),
        ("2001\u20132020", "2001-2020"),
        ("Griffies et\u00a0al.", "Griffies et al."),
        ("Camargo, S. J., \u2026 & Zhao, M.", "Camargo, S. J., ... & Zhao, M."),
        # Including in DOIs, which must stay valid
        (
            "https://doi.org/10.1175/JPO\u2010D\u201014\u20100259.1",
            "https://doi.org/10.1175/JPO-D-14-0259.1",
        ),
        # Everything else goes to LaTeX
        ("Universit\u00e9 de Montr\u00e9al", "Universit\\'e de Montr\\'eal"),
        ("Me\u0301te\u0301o-France", "M\\'et\\'eo-France"),
        ("Gie\u00dfen", "Gie{\\ss}en"),
        ("Troms\u00f8", "Troms{\\o}"),
        ("Nyg\u00e5rdsh\u00f8yden", "Nyg\\r{a}rdsh{\\o}yden"),
        ("\u0130T\u00dc", '\\.IT\\"U'),
        ("Kish\u014dkenky\u016bsho", "Kish\\={o}kenky\\={u}sho"),
        ("Dr\u017eavni", "Dr\\v{z}avni"),
        ("Alterskj\u00e6r", "Alterskj{\\ae}r"),
        ("0.5\u00b0", "0.5{\\textdegree}"),
        ("(\u00bc\u00b0; 75 layers)", "({\\textonequarter}{\\textdegree}; 75 layers)"),
        ("CO\u2082, CH\u2084", "CO\\ensuremath{_2}, CH\\ensuremath{_4}"),
        # ASCII is never touched
        ("50% & a_b $x$ ~ \\", "50% & a_b $x$ ~ \\"),
        # Characters with no LaTeX equivalent are kept
        ("\u4e2d\u56fd\u79d1\u5b66\u9662", "\u4e2d\u56fd\u79d1\u5b66\u9662"),
    ),
)
def test_to_ascii_latex(value, expected):
    assert to_ascii_latex(value) == expected
    # Applying it again changes nothing
    assert to_ascii_latex(expected) == expected


def test_dumps_json_has_no_unicode_escapes():
    payload = {
        "description": "fire\u2019s \u201crole\u201d",
        "labels": ["M\u00e9t\u00e9o-France", "\u4e2d\u56fd"],
        "tier": 1,
        "parent": None,
    }
    # Sanity check of the failure mode we're avoiding
    assert "\\u2019" in json.dumps(payload)

    res = dumps_json(payload)

    assert "\\u" not in res
    assert json.loads(res) == {
        "description": 'fire\'s "role"',
        "labels": ["M\\'et\\'eo-France", "\u4e2d\u56fd"],
        "tier": 1,
        "parent": None,
    }
