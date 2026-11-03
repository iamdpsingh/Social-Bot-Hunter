"""Feature vector schemas."""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel


class AccountFeatureResponse(BaseModel):
    """Computed account feature record view."""

    feature_name: str
    feature_version: str
    category: str
    value: float | None = None
    is_available: bool
    details: dict[str, Any] = {}
