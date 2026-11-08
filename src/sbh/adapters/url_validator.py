"""SSRF-safe social media profile URL validator and canonical normalizer."""

from __future__ import annotations

import ipaddress
import re
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

_YT_HANDLE_RE = re.compile(r"^@?([a-zA-Z0-9_\-\.]{3,30})$")
_YT_CHANNEL_ID_RE = re.compile(r"^UC[a-zA-Z0-9_\-]{22}$")


def _validate_ssrf_safety(raw_url: str) -> None:
    """Validate that URL does not target local, private or cloud metadata IPs."""
    if len(raw_url) > _MAX_URL_LENGTH:
        raise InvalidUrlError("URL exceeds maximum length of 2048 characters", url=raw_url)

    parsed = urlparse(raw_url)
    if not parsed.scheme:
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
        pass


def _parse_youtube_url(url: str) -> ProfileUrlInfo:
    """Parse YouTube channel URL, handle, or canonical ID."""
    url = url.strip()
    if url.startswith("@"):
        match = _YT_HANDLE_RE.match(url)
        if not match:
            raise InvalidUrlError(f"Invalid YouTube handle '{url}'", url=url, platform="youtube")
        handle = match.group(1).lower()
        return ProfileUrlInfo(
            platform=Platform.YOUTUBE,
            handle=f"@{handle}",
            canonical_url=f"https://www.youtube.com/@{handle}",
            raw_url=url,
            url_type=UrlType.HANDLE,
            is_canonical=True,
        )

    parsed = urlparse(url)
    path = parsed.path.strip("/")
    parts = path.split("/") if path else []

    if parts and parts[0].startswith("@"):
        match = _YT_HANDLE_RE.match(parts[0])
        if not match:
            raise InvalidUrlError(f"Invalid YouTube handle '{parts[0]}'", url=url, platform="youtube")
        handle = match.group(1).lower()
        is_canonical = (
            parsed.netloc.lower() == "www.youtube.com"
            and not parsed.query
            and len(parts) == 1
        )
        return ProfileUrlInfo(
            platform=Platform.YOUTUBE,
            handle=f"@{handle}",
            canonical_url=f"https://www.youtube.com/@{handle}",
            raw_url=url,
            url_type=UrlType.HANDLE,
            is_canonical=is_canonical,
        )

    raise InvalidUrlError("Unsupported YouTube profile format", url=url, platform="youtube")
