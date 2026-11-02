"""Common query filter parameter schemas."""

from __future__ import annotations

from pydantic import BaseModel, Field


class AccountFilterParams(BaseModel):
    """Account query filtering criteria."""
    min_risk: float | None = Field(default=None, ge=0, le=100)
    is_verified: bool | None = None
    platform: str | None = None
