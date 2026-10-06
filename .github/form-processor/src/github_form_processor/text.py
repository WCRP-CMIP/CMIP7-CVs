"""Text normalisation helpers for the files written into the CVs."""

from __future__ import annotations

import json
import unicodedata
from typing import Any

# Typographic characters (typically introduced by copy-pasting from word
# processors) and their plain ASCII equivalents.
_ASCII_REPLACEMENTS = str.maketrans(
    {
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
        "\u2010": "-",  # hyphen
        "\u2011": "-",  # non-breaking hyphen
        "\u2012": "-",  # figure dash
        "\u2013": "-",  # en dash
        "\u2014": "-",  # em dash
        "\u2015": "-",  # horizontal bar
        "\u2212": "-",  # minus sign
        "\u00a0": " ",  # no-break space
        "\u2009": " ",  # thin space
        "\u202f": " ",  # narrow no-break space
        "\u200b": "",  # zero width space
        "\ufeff": "",  # zero width no-break space (byte order mark)
        "\u00ad": "",  # soft hyphen
        "\u2022": "-",  # bullet
    }
)


def to_plain_text(value: str) -> str:
    r"""Convert typographic punctuation in a string to plain ASCII.

    Curly quotes, dashes, special spaces etc. are replaced with their plain
    ASCII equivalents. Letters (e.g. accented letters in names) are kept as is,
    but normalised to their composed form.

    >>> to_plain_text("fire\u2019s \u201crole\u201d \u2013 1850\u20131900")
    'fire\'s "role" - 1850-1900'
    """
    return unicodedata.normalize("NFC", value.translate(_ASCII_REPLACEMENTS))


def to_plain_text_recursive(value: Any) -> Any:
    r"""Apply [to_plain_text][] to every string (keys included) in a JSON-like value.

    >>> to_plain_text_recursive({"a\u2019": ["\u2018b\u2019", 1, None]})
    {"a'": ["'b'", 1, None]}
    """
    if isinstance(value, str):
        return to_plain_text(value)

    if isinstance(value, dict):
        return {
            to_plain_text_recursive(k): to_plain_text_recursive(v)
            for k, v in value.items()
        }

    if isinstance(value, (list, tuple)):
        return [to_plain_text_recursive(v) for v in value]

    return value


def dumps_json(payload: Any, indent: int = 4) -> str:
    r"""Serialise a CV entry as JSON, converting its text to plain text first.

    Typographic punctuation is converted to ASCII (see [to_plain_text][])
    and any remaining non-ASCII characters (e.g. accented letters in names)
    are written as UTF-8 rather than as escape sequences like `\u00e9`,
    so the files (and pull request diffs) stay readable.

    >>> print(dumps_json({"description": "fire\u2019s role"}, indent=2), end="")
    {
      "description": "fire's role"
    }
    """
    return (
        json.dumps(to_plain_text_recursive(payload), indent=indent, ensure_ascii=False)
        + "\n"
    )
