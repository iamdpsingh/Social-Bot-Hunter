"""Domain exceptions for platform adapters and integrations."""

from __future__ import annotations


class AdapterError(Exception):
    """Base exception for all adapter errors."""

    def __init__(self, message: str, platform: str | None = None) -> None:
        super().__init__(message)
        self.platform = platform


class InvalidUrlError(AdapterError):
    """Raised when a provided profile or resource URL is malformed, unsafe, or invalid."""

    def __init__(self, message: str, url: str, platform: str | None = None) -> None:
        super().__init__(message, platform)
        self.url = url


class UnsupportedPlatformError(AdapterError):
    """Raised when an operation is requested on an unsupported platform."""


class QuotaExceededError(AdapterError):
    """Raised when an API quota limit has been reached."""

    def __init__(
        self,
        message: str,
        platform: str,
        units_used: int,
        daily_limit: int,
        resets_at: str | None = None,
    ) -> None:
        super().__init__(message, platform)
        self.units_used = units_used
        self.daily_limit = daily_limit
        self.resets_at = resets_at


class RateLimitExceededError(AdapterError):
    """Raised when HTTP 429 Too Many Requests is received from a platform API."""

    def __init__(
        self,
        message: str,
        platform: str,
        retry_after_seconds: float = 60.0,
        endpoint: str | None = None,
    ) -> None:
        super().__init__(message, platform)
        self.retry_after_seconds = retry_after_seconds
        self.endpoint = endpoint


class AuthenticationError(AdapterError):
    """Raised when API credentials are missing, revoked, expired, or lack required scope."""


class EntityNotFoundError(AdapterError):
    """Raised when a requested channel, user, or resource does not exist on the platform."""

    def __init__(self, message: str, platform: str, entity_id: str) -> None:
        super().__init__(message, platform)
        self.entity_id = entity_id
