"""Scan job schemas."""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field


class CreateScanRequest(BaseModel):
    """Investigation scan submission request."""
    platform: str = Field(pattern="^(instagram|x|tiktok|youtube|linkedin)$")
    target_account: str
    scope: str = Field(default="standard", pattern="^(quick|standard|deep|comprehensive)$")
    config_overrides: dict[str, Any] = Field(default_factory=dict)


class ScanResponse(BaseModel):
    """Investigation scan response."""
    id: str
    platform: str
    status: str
    data_origin: str
    requested_by: str
    created_at: str
    reference_time: str
