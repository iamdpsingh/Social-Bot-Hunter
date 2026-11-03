"""Account representation schemas."""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel


class AccountResponse(BaseModel):
    """Account profile view."""

    id: str
    platform: str
    platform_account_id: str
    username: str | None = None
    display_name: str | None = None
    first_observed_at: str
    last_observed_at: str
    metadata: dict[str, Any] = {}
