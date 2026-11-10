"""Platform Adapters package for Social Bot Hunter."""

from sbh.adapters.errors import (
    AdapterError,
    AuthenticationError,
    EntityNotFoundError,
    InvalidUrlError,
    PlatformQuotaExceededError,
    QuotaExceededError,
    RateLimitExceededError,
    UnsupportedPlatformError,
)
from sbh.adapters.instagram import InstagramAdapter
from sbh.adapters.instagram_client import InstagramApiClient, MockInstagramClient
from sbh.adapters.linkedin import LinkedInAdapter
from sbh.adapters.linkedin_client import LinkedInApiClient, MockLinkedInClient
from sbh.adapters.quota import PlatformQuotaTracker
from sbh.adapters.rate_limiter import EndpointRateLimiter
from sbh.adapters.registry import AdapterRegistry, default_registry
from sbh.adapters.telemetry import AdapterTelemetryManager, telemetry_manager
from sbh.adapters.tiktok import TikTokAdapter
from sbh.adapters.tiktok_client import MockTikTokClient, TikTokApiClient
from sbh.adapters.url_validator import ProfileUrlInfo, UrlType, validate_profile_url
from sbh.adapters.x import XAdapter
from sbh.adapters.youtube import YouTubeAdapter

__all__ = [
    "AdapterError",
    "AdapterRegistry",
    "AdapterTelemetryManager",
    "AuthenticationError",
    "EndpointRateLimiter",
    "EntityNotFoundError",
    "InstagramAdapter",
    "InstagramApiClient",
    "InvalidUrlError",
    "LinkedInAdapter",
    "LinkedInApiClient",
    "MockInstagramClient",
    "MockLinkedInClient",
    "MockTikTokClient",
    "PlatformQuotaExceededError",
    "PlatformQuotaTracker",
    "ProfileUrlInfo",
    "QuotaExceededError",
    "RateLimitExceededError",
    "TikTokAdapter",
    "TikTokApiClient",
    "UnsupportedPlatformError",
    "UrlType",
    "XAdapter",
    "YouTubeAdapter",
    "default_registry",
    "telemetry_manager",
    "validate_profile_url",
]
