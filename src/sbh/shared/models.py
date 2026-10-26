"""Small value types shared between storage, features and graph analysis."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Post:
    author: str  # platform account id
    ts: float  # publication time, epoch seconds (UTC)
    content_hash: str | None
    simhash: int | None
