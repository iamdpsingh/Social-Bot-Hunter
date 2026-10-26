"""Timestamp handling. All stored timestamps are UTC ISO-8601 strings with a fixed width.

A fixed-width format means lexicographic order equals chronological order, which keeps
comparisons correct on both SQLite (text) and PostgreSQL (timestamptz).
"""

from __future__ import annotations

from datetime import UTC, datetime

_EARLIEST_PLAUSIBLE = datetime(2000, 1, 1, tzinfo=UTC)


def utcnow() -> datetime:
    return datetime.now(UTC)


def iso_utc(dt: datetime) -> str:
    if dt.tzinfo is None:
        raise ValueError("naive datetime cannot be serialised; attach a timezone first")
    return dt.astimezone(UTC).strftime("%Y-%m-%dT%H:%M:%S.%fZ")


def parse_timestamp(value: object) -> datetime:
    """Parse a timestamp that carries an explicit timezone. Naive values are rejected.

    Rejecting naive timestamps avoids silently guessing a timezone, which would corrupt
    any temporal-synchronisation analysis.
    """
    if isinstance(value, datetime):
        dt = value
    elif isinstance(value, str):
        text = value.strip()
        if not text:
            raise ValueError("empty timestamp")
        try:
            dt = datetime.fromisoformat(text)
        except ValueError as exc:
            raise ValueError(f"not an ISO-8601 timestamp: {text[:40]!r}") from exc
    else:
        raise ValueError(f"unsupported timestamp type: {type(value).__name__}")
    if dt.tzinfo is None:
        raise ValueError("timestamp has no timezone offset")
    dt = dt.astimezone(UTC)
    if dt < _EARLIEST_PLAUSIBLE:
        raise ValueError("timestamp is implausibly old (before 2000-01-01)")
    return dt


def from_db(value: object) -> datetime | None:
    """Convert a database value (ISO string on SQLite, datetime on PostgreSQL) to datetime."""
    if value is None:
        return None
    if isinstance(value, datetime):
        return value if value.tzinfo else value.replace(tzinfo=UTC)
    return parse_timestamp(value)
