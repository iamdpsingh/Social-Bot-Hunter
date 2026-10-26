"""Input sanitisation and export-safety helpers."""

from __future__ import annotations

import unicodedata

_FORMULA_PREFIXES = ("=", "+", "-", "@", "\t", "\r")


def clean_text(value: str, max_len: int) -> str:
    """Strip control characters and surrounding whitespace, then enforce a length limit.

    Raises ValueError rather than truncating, because silent truncation would change
    identifiers and content fingerprints without a trace.
    """
    cleaned = "".join(
        ch for ch in value if ch in ("\n", "\t") or unicodedata.category(ch)[0] != "C"
    ).strip()
    if len(cleaned) > max_len:
        raise ValueError(f"value longer than {max_len} characters")
    return cleaned


def csv_safe_cell(value: object) -> str:
    """Neutralise spreadsheet formula injection for exported CSV cells.

    Imported usernames and display names are attacker-controlled. A cell starting with
    '=' can execute as a formula when the export is opened in a spreadsheet application.
    """
    text = "" if value is None else str(value)
    if text.startswith(_FORMULA_PREFIXES):
        return "'" + text
    return text
