"""SSRF-safe social media profile URL validator and canonical normalizer."""

from __future__ import annotations

import ipaddress
from dataclasses import dataclass
from enum import StrEnum
from urllib.parse import urlparse

from sbh.adapters.errors import InvalidUrlError
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


_ALLOWED_SCHEMES = frozenset({"http", "https"})
_FORBIDDEN_HOSTNAMES = frozenset({"localhost", "127.0.0.1", "0.0.0.0", "169.254.169.254"})
_MAX_URL_LENGTH = 2048


def _validate_ssrf_safety(raw_url: str) -> None:
    """Validate that URL does not target local, private or cloud metadata IPs."""
    if len(raw_url) > _MAX_URL_LENGTH:
        raise InvalidUrlError("URL exceeds maximum length of 2048 characters", url=raw_url)

    parsed = urlparse(raw_url)
    if not parsed.scheme:
        # Bare handle or relative path
        return

    if parsed.scheme.lower() not in _ALLOWED_SCHEMES:
        raise InvalidUrlError(
            f"Unsupported scheme '{parsed.scheme}': only http and https are allowed",
            url=raw_url,
        )

    hostname = (parsed.hostname or "").lower()
    if not hostname:
        raise InvalidUrlError("URL is missing a valid hostname", url=raw_url)

    if hostname in _FORBIDDEN_HOSTNAMES:
        raise InvalidUrlError(f"Prohibited hostname '{hostname}' rejected for security", url=raw_url)

    try:
        ip = ipaddress.ip_address(hostname)
        if ip.is_private or ip.is_loopback or ip.is_link_local:
            raise InvalidUrlError(f"Private IP address '{hostname}' is not permitted", url=raw_url)
    except ValueError:
        # Hostname is a standard domain name, not an IP literal
        pass
