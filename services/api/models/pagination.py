"""Cursor and offset pagination models."""

from __future__ import annotations

from pydantic import BaseModel, Field


class PaginationQueryParams(BaseModel):
    """Standard pagination URL query parameters."""

    limit: int = Field(default=50, ge=1, le=500)
    offset: int = Field(default=0, ge=0)
