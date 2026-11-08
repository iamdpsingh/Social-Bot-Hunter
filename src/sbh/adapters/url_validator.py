"""SSRF-safe social media profile URL validator and canonical normalizer."""

from __future__ import annotations

import ipaddress
import re
from dataclasses import dataclass
from enum import StrEnum
from urllib.parse import urlparse

from sbh.adapters.errors import InvalidUrlError, UnsupportedPlatformError
from sbh.contracts.platforms import Platform


class UrlType(StrEnum):
    HANDLE = "handle"
    CHANNEL_ID = "channel_id"
    CUSTOM_URL = "custom_url"
    LEGACY_USER = "legacy_user"
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
_YT_CUSTOM_NAME_RE = re.compile(r"^[a-zA-Z0-9_\-\.]{3,50}$")

_X_HANDLE_RE = re.compile(r"^@?([a-zA-Z0-9_]{1,15})$")
_X_RESERVED_NAMES = frozenset(
    {
        "home",
        "explore",
        "notifications",
        "messages",
        "bookmarks",
        "settings",
        "search",
        "tos",
        "privacy",
        "about",
        "login",
        "logout",
        "i",
        "intent",
        "download",
    }
)


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

    if "watch?v=" in url or "/shorts/" in url or "youtu.be/" in url:
        raise InvalidUrlError(
            "Expected a YouTube channel or profile URL, but received a video watch link.",
            url=url,
            platform="youtube",
        )

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

    if _YT_CHANNEL_ID_RE.match(url):
        return ProfileUrlInfo(
            platform=Platform.YOUTUBE,
            handle=url,
            canonical_url=f"https://www.youtube.com/channel/{url}",
            raw_url=url,
            url_type=UrlType.CHANNEL_ID,
            channel_id=url,
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

    if len(parts) >= 2 and parts[0] == "channel":
        channel_id = parts[1]
        if not _YT_CHANNEL_ID_RE.match(channel_id):
            raise InvalidUrlError(
                f"Invalid YouTube 24-character channel ID '{channel_id}'",
                url=url,
                platform="youtube",
            )
        is_canonical = (
            parsed.netloc.lower() == "www.youtube.com"
            and not parsed.query
            and len(parts) == 2
        )
        return ProfileUrlInfo(
            platform=Platform.YOUTUBE,
            handle=channel_id,
            canonical_url=f"https://www.youtube.com/channel/{channel_id}",
            raw_url=url,
            url_type=UrlType.CHANNEL_ID,
            channel_id=channel_id,
            is_canonical=is_canonical,
        )

    if len(parts) >= 2 and parts[0] in ("c", "user"):
        custom_name = parts[1]
        if not _YT_CUSTOM_NAME_RE.match(custom_name):
            raise InvalidUrlError(
                f"Invalid YouTube name '{custom_name}'",
                url=url,
                platform="youtube",
            )
        url_type = UrlType.CUSTOM_URL if parts[0] == "c" else UrlType.LEGACY_USER
        return ProfileUrlInfo(
            platform=Platform.YOUTUBE,
            handle=custom_name,
            canonical_url=f"https://www.youtube.com/{parts[0]}/{custom_name}",
            raw_url=url,
            url_type=url_type,
            is_canonical=False,
        )

    raise InvalidUrlError("Unsupported YouTube profile format", url=url, platform="youtube")


def _parse_x_url(url: str) -> ProfileUrlInfo:
    """Parse X (Twitter) profile URL or username."""
    url = url.strip()

    if url.startswith("@"):
        match = _X_HANDLE_RE.match(url)
        if not match:
            raise InvalidUrlError(
                f"Invalid X username '{url}': must be 1-15 alphanumeric characters or underscores",
                url=url,
                platform="x",
            )
        handle = match.group(1).lower()
        if handle in _X_RESERVED_NAMES:
            raise InvalidUrlError(f"'{handle}' is a reserved X system route", url=url, platform="x")
        return ProfileUrlInfo(
            platform=Platform.X,
            handle=handle,
            canonical_url=f"https://x.com/{handle}",
            raw_url=url,
            url_type=UrlType.HANDLE,
            is_canonical=True,
        )

    parsed = urlparse(url)
    path = parsed.path.strip("/")
    parts = path.split("/") if path else []

    if not parts:
        raise InvalidUrlError("No username found in X URL", url=url, platform="x")

    username = parts[0].lstrip("@")
    match = _X_HANDLE_RE.match(username)
    if not match:
        raise InvalidUrlError(
            f"Invalid X username '{username}': must be 1-15 alphanumeric characters",
            url=url,
            platform="x",
        )

    handle = match.group(1).lower()
    if handle in _X_RESERVED_NAMES:
        raise InvalidUrlError(f"'{handle}' is a reserved X system route", url=url, platform="x")

    url_type = UrlType.STATUS_LINK if len(parts) >= 3 and parts[1] == "status" else UrlType.HANDLE

    is_canonical = (
        parsed.netloc.lower() == "x.com"
        and not parsed.query
        and len(parts) == 1
        and not parsed.fragment
    )

    return ProfileUrlInfo(
        platform=Platform.X,
        handle=handle,
        canonical_url=f"https://x.com/{handle}",
        raw_url=url,
        url_type=url_type,
        is_canonical=is_canonical,
    )


def validate_profile_url(
    url: str,
    platform_hint: Platform | None = None,
) -> ProfileUrlInfo:
    """Validate and canonicalize a social media profile URL or identifier.

    Autodetects platform from host or syntax when platform_hint is omitted.
    Applies SSRF prevention, path sanitization, and canonical link generation.
    """
    clean_url = url.strip()
    if not clean_url:
        raise InvalidUrlError("Profile URL or identifier cannot be empty", url=url)

    _validate_ssrf_safety(clean_url)

    # Detect platform if not hinted
    platform = platform_hint
    if platform is None:
        parsed = urlparse(clean_url)
        host = (parsed.hostname or "").lower()

        if "youtube.com" in host or "youtu.be" in host or clean_url.startswith("UC"):
            platform = Platform.YOUTUBE
        elif "twitter.com" in host or "x.com" in host or clean_url.startswith("@"):
            platform = Platform.X
        elif "bsky.app" in host or clean_url.startswith("did:plc:"):
            raise UnsupportedPlatformError(
                "Bluesky is not currently configured for live adapter collection."
            )
        elif "instagram.com" in host:
            raise UnsupportedPlatformError(
                "Instagram live collection adapter is not yet configured (Phase 6)."
            )
        elif "tiktok.com" in host:
            raise UnsupportedPlatformError(
                "TikTok live collection adapter is not yet configured (Phase 6)."
            )
        elif "linkedin.com" in host:
            raise UnsupportedPlatformError(
                "LinkedIn live collection adapter is not yet configured (Phase 6)."
            )
        else:
            raise UnsupportedPlatformError(
                f"Unable to determine platform for identifier '{clean_url}'",
            )

    if platform == Platform.YOUTUBE:
        return _parse_youtube_url(clean_url)
    elif platform == Platform.X:
        return _parse_x_url(clean_url)
    else:
        raise UnsupportedPlatformError(f"Platform '{platform.value}' has no active adapter.")
