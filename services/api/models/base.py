"""Base API schemas and common primitives."""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field


class ApiModel(BaseModel):
    """Base model enforcing strict configuration."""
    model_config = ConfigDict(extra="forbid", populate_by_name=True)


class PaginationMeta(ApiModel):
    """Standard pagination metadata envelope."""
    total: int = Field(ge=0, description="Total matching records count")
    limit: int = Field(gt=0, le=1000, description="Page limit requested")
    offset: int = Field(ge=0, description="Page offset")


class ApiResponse(ApiModel):
    """Generic status response payload."""
    status: str = Field(default="ok", description="Status code indicator")
    message: str | None = Field(default=None, description="Optional informational message")
