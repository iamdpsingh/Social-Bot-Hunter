"""Platform capability schemas."""

from __future__ import annotations

from pydantic import BaseModel


class OperationCapability(BaseModel):
    """Operation support matrix item."""
    operation: str
    status: str
    supported: bool
    endpoint: str | None = None
    limitation: str | None = None


class PlatformCapabilityResponse(BaseModel):
    """Platform capabilities description."""
    platform: str
    operations: list[OperationCapability]
