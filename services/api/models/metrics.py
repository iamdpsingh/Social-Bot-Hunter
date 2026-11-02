"""Operational metrics schemas."""

from __future__ import annotations

from pydantic import BaseModel


class ServiceMetricsResponse(BaseModel):
    """Runtime service performance metrics."""
    uptime_seconds: float
    total_requests: int
    active_scans: int
    error_count: int
