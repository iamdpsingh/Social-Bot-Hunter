"""Webhook notification schemas."""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel


class WebhookPayload(BaseModel):
    """Scan completion webhook payload."""
    event: str = "scan.completed"
    scan_id: str
    status: str
    summary: dict[str, Any] = {}
