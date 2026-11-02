"""Platform-specific metadata schemas."""

from __future__ import annotations

from pydantic import BaseModel


class PlatformMetadata(BaseModel):
    """Generic platform metadata holder."""
    platform_name: str
    api_version: str = "v1"
