"""Tests for unsupported platform rejection in URL validation."""

from __future__ import annotations

import pytest

from sbh.adapters.errors import InvalidUrlError, UnsupportedPlatformError
from sbh.adapters.url_validator import validate_profile_url


def test_bluesky_url_rejected_with_unsupported_error() -> None:
    with pytest.raises(UnsupportedPlatformError, match="Bluesky is not currently configured"):
        validate_profile_url("https://bsky.app/profile/alice.bsky.social")


def test_bluesky_did_rejected() -> None:
    with pytest.raises(InvalidUrlError, match="Unsupported scheme 'did'"):
        validate_profile_url("did:plc:z72i7hdynmk6r22z27h6tvur")


def test_instagram_url_rejected() -> None:
    with pytest.raises(UnsupportedPlatformError, match="Instagram live collection adapter is not yet configured"):
        validate_profile_url("https://www.instagram.com/natgeo")


def test_tiktok_url_rejected() -> None:
    with pytest.raises(UnsupportedPlatformError, match="TikTok live collection adapter is not yet configured"):
        validate_profile_url("https://www.tiktok.com/@creator")


def test_linkedin_url_rejected() -> None:
    with pytest.raises(UnsupportedPlatformError, match="LinkedIn live collection adapter is not yet configured"):
        validate_profile_url("https://www.linkedin.com/in/satyanadella")
