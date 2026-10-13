r"""Text normalisation helpers for the files written into the CVs.

The CVs only contain ASCII. Text is converted to ASCII in two steps
(see [to_ascii_latex][]):

1. Typographic characters (typically introduced by copy-pasting from word
   processors, e.g. curly quotes, dashes and special spaces) are replaced
   with their plain ASCII equivalents, as listed in [ASCII_REPLACEMENTS][].
   To change how such a character is handled, add or edit it there.
2. Every other non-ASCII character (e.g. accented letters in names,
   symbols like the degree sign) is encoded as its LaTeX equivalent
   using [pylatexenc](https://pypi.org/project/pylatexenc/),
   e.g. an e with an acute accent becomes `\'e`.
   Characters which have no LaTeX equivalent
   (e.g. Chinese characters in names in their native script) are kept as is.
   They are flagged by the CI check of the CVs
   (`scripts/check-cv-entries-are-ascii.py`).

ASCII text is never altered by the LaTeX encoding,
i.e. characters like `%`, `&`, `_` and `$` are not escaped.

If you change the conversion here, also update the copy
in the WCRP-universe's `scripts/ascii_latex.py`.
"""

from __future__ import annotations

import json
import unicodedata
from typing import Any

from pylatexenc.latexencode import UnicodeToLatexEncoder

ASCII_REPLACEMENTS: dict[str, str] = {
    # Quotation marks
    "\u2018": "'",  # left single quotation mark
    "\u2019": "'",  # right single quotation mark
    "\u201a": "'",  # single low-9 quotation mark
    "\u201b": "'",  # single high-reversed-9 quotation mark
    "\u2032": "'",  # prime
    "\u00b4": "'",  # acute accent
    "\u201c": '"',  # left double quotation mark
    "\u201d": '"',  # right double quotation mark
    "\u201e": '"',  # double low-9 quotation mark
    "\u201f": '"',  # double high-reversed-9 quotation mark
    "\u2033": '"',  # double prime
    "\u00ab": '"',  # left-pointing double angle quotation mark
    "\u00bb": '"',  # right-pointing double angle quotation mark
    # Dashes and hyphens
    "\u2010": "-",  # hyphen
    "\u2011": "-",  # non-breaking hyphen
    "\u2012": "-",  # figure dash
    "\u2013": "-",  # en dash
    "\u2014": "-",  # em dash
    "\u2015": "-",  # horizontal bar
    "\u2212": "-",  # minus sign
    "\u00ad": "",  # soft hyphen
    # Spaces
    "\u00a0": " ",  # no-break space
    "\u2009": " ",  # thin space
    "\u202f": " ",  # narrow no-break space
    "\u200b": "",  # zero width space
    "\ufeff": "",  # zero width no-break space (byte order mark)
    # Other punctuation
    "\u2022": "-",  # bullet
    "\u2026": "...",  # horizontal ellipsis
}
"""
Typographic characters and the plain ASCII they are replaced with

Any non-ASCII character not listed here is encoded as LaTeX instead.
"""

_ASCII_TRANSLATION = str.maketrans(ASCII_REPLACEMENTS)

_LATEX_ENCODER = UnicodeToLatexEncoder(
    # Leave ASCII (e.g. `%`, `&`, `_`, `$`, `\`) exactly as it is
    non_ascii_only=True,
    # Only add braces where they are needed to keep the LaTeX valid,
    # e.g. sharp s becomes `{\ss}` but an e with an acute accent becomes `\'e`
    replacement_latex_protection="braces",
    # Characters without a LaTeX equivalent are kept
    # (and flagged by the CI check of the CVs)
    unknown_char_policy="keep",
    unknown_char_warning=True,
)


def to_plain_text(value: str) -> str:
    r"""Convert typographic punctuation in a string to plain ASCII.

    Curly quotes, dashes, special spaces etc. are replaced with their plain
    ASCII equivalents (see [ASCII_REPLACEMENTS][]). Letters (e.g. accented
    letters in names) are kept as is, but normalised to their composed form.

    >>> to_plain_text("fire\u2019s \u201crole\u201d \u2013 1850\u20131900")
    'fire\'s "role" - 1850-1900'
    """
    return unicodedata.normalize("NFC", value.translate(_ASCII_TRANSLATION))


def to_ascii_latex(value: str) -> str:
    r"""Convert a string to ASCII, encoding non-ASCII characters as LaTeX.

    Typographic punctuation is first converted to plain ASCII
    (see [to_plain_text][]), then all other non-ASCII characters
    are encoded as their LaTeX equivalent.
    Characters with no LaTeX equivalent are kept as is.

    Applying this function to its own output changes nothing,
    so it is safe to apply to text that has already been converted.

    >>> print(to_ascii_latex("Universit\u00e9 de Montr\u00e9al"))
    Universit\'e de Montr\'eal
    >>> print(to_ascii_latex("Justus-Liebig-Universit\u00e4t Gie\u00dfen"))
    Justus-Liebig-Universit\"at Gie{\ss}en
    >>> print(to_ascii_latex("0.5\u00b0 resolution, CO\u2082"))
    0.5{\textdegree} resolution, CO\ensuremath{_2}
    >>> print(to_ascii_latex("2001\u20132020, the Earth\u2019s 50% & a_b"))
    2001-2020, the Earth's 50% & a_b
    >>> print(to_ascii_latex("\u4e2d\u56fd\u79d1\u5b66\u9662"))
    \u4e2d\u56fd\u79d1\u5b66\u9662
    """
    return _LATEX_ENCODER.unicode_to_latex(to_plain_text(value))


def to_ascii_latex_recursive(value: Any) -> Any:
    r"""Apply [to_ascii_latex][] to every string (keys included) in a JSON-like value.

    >>> to_ascii_latex_recursive({"a\u2019": ["\u00e9", 1, None]})
    {"a'": ["\\'e", 1, None]}
    """
    if isinstance(value, str):
        return to_ascii_latex(value)

    if isinstance(value, dict):
        return {
            to_ascii_latex_recursive(k): to_ascii_latex_recursive(v)
            for k, v in value.items()
        }

    if isinstance(value, (list, tuple)):
        return [to_ascii_latex_recursive(v) for v in value]

    return value


def dumps_json(payload: Any, indent: int = 4) -> str:
    r"""Serialise a CV entry as JSON, converting its text to ASCII first.

    Text is converted with [to_ascii_latex][].
    Any remaining non-ASCII characters (i.e. those with no LaTeX equivalent)
    are written as UTF-8 rather than as escape sequences like `\u4e2d`,
    so the files (and pull request diffs) stay readable.

    >>> print(dumps_json({"description": "fire\u2019s role"}, indent=2), end="")
    {
      "description": "fire's role"
    }
    """
    return (
        json.dumps(to_ascii_latex_recursive(payload), indent=indent, ensure_ascii=False)
        + "\n"
    )
