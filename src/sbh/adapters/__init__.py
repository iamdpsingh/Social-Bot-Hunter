"""Platform adapters and integration layer for Social Bot Hunter.

Provides live adapters for official social platform APIs (YouTube Data API v3,
X API v2), rate limiting, quota tracking, and SSRF-safe URL validation.
"""

from __future__ import annotations

from sbh.adapters.errors import (
    AdapterError,
    AuthenticationError,
    EntityNotFoundError,
    InvalidUrlError,
    QuotaExceededError,
    RateLimitExceededError,
    UnsupportedPlatformError,
)
from sbh.adapters.quota import PlatformQuotaTracker
from sbh.adapters.url_validator import ProfileUrlInfo, UrlType, validate_profile_url
from sbh.adapters.youtube import YouTubeAdapter
from sbh.adapters.youtube_client import MockYouTubeClient, YouTubeApiClient

__all__ = [
    "AdapterError",
    "AuthenticationError",
    "EntityNotFoundError",
    "InvalidUrlError",
    "MockYouTubeClient",
    "PlatformQuotaTracker",
    "ProfileUrlInfo",
    "QuotaExceededError",
    "RateLimitExceededError",
    "UnsupportedPlatformError",
    "UrlType",
    "YouTubeAdapter",
    "YouTubeApiClient",
    "validate_profile_url",
]
