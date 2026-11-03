"""Content item schemas."""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel


class ContentResponse(BaseModel):
    """Social media post observation view."""

    id: str
    scan_id: str
    platform: str
    platform_content_id: str
    author_account_id: str
    published_at: str
    like_count: int | None = None
    reply_count: int | None = None
    share_count: int | None = None
    metadata: dict[str, Any] = {}
