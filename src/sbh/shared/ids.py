"""Identifier generation. IDs are UUID strings stored as TEXT for SQLite/PostgreSQL portability."""

from __future__ import annotations

import uuid


def new_id() -> str:
    return str(uuid.uuid4())
