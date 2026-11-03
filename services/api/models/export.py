"""Report export schemas."""

from __future__ import annotations

from pydantic import BaseModel, Field


class ExportRequest(BaseModel):
    """Export specification request."""

    format: str = Field(pattern="^(json|csv|pdf)$")
    include_raw: bool = False
