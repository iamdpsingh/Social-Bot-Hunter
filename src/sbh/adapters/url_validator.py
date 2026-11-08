"""SSRF-safe social media profile URL validator and canonical normalizer."""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum

from sbh.contracts.platforms import Platform


class UrlType(StrEnum):
    HANDLE = "handle"
    CHANNEL_ID = "channel_id"
    CUSTOM_URL = "custom_url"
    LEGACY_USER = "legacy_user"
    DID = "did"
    STATUS_LINK = "status_link"


@dataclass(frozen=True)
class ProfileUrlInfo:
    """Parsed and validated profile URL information."""

    platform: Platform
    handle: str
    canonical_url: str
    raw_url: str
    url_type: UrlType
    channel_id: str | None = None
    is_canonical: bool = True
