"""Service health check schemas."""

from __future__ import annotations

from pydantic import BaseModel


class HealthStatusResponse(BaseModel):
    """System health response."""
    status: str = "ok"
    version: str
    environment: str = "local"
    database_connected: bool = True
