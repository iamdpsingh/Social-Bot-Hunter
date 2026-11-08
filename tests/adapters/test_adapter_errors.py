"""Tests for adapter domain exceptions."""

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


def test_adapter_error_hierarchy() -> None:
    assert issubclass(InvalidUrlError, AdapterError)
    assert issubclass(UnsupportedPlatformError, AdapterError)
    assert issubclass(QuotaExceededError, AdapterError)
    assert issubclass(RateLimitExceededError, AdapterError)
    assert issubclass(AuthenticationError, AdapterError)
    assert issubclass(EntityNotFoundError, AdapterError)


def test_invalid_url_error_attributes() -> None:
    err = InvalidUrlError("Malformed URL", url="https://invalid", platform="youtube")
    assert str(err) == "Malformed URL"
    assert err.url == "https://invalid"
    assert err.platform == "youtube"


def test_quota_exceeded_error_attributes() -> None:
    err = QuotaExceededError(
        "Daily limit reached",
        platform="youtube",
        units_used=10000,
        daily_limit=10000,
        resets_at="2026-11-09T00:00:00Z",
    )
    assert err.platform == "youtube"
    assert err.units_used == 10000
    assert err.daily_limit == 10000
    assert err.resets_at == "2026-11-09T00:00:00Z"


def test_rate_limit_exceeded_error_attributes() -> None:
    err = RateLimitExceededError(
        "Rate limit exceeded",
        platform="x",
        retry_after_seconds=900.0,
        endpoint="/2/users/by/username",
    )
    assert err.platform == "x"
    assert err.retry_after_seconds == 900.0
    assert err.endpoint == "/2/users/by/username"


def test_entity_not_found_error_attributes() -> None:
    err = EntityNotFoundError("User not found", platform="x", entity_id="@unknown")
    assert err.platform == "x"
    assert err.entity_id == "@unknown"
