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


from sbh.contracts.platforms import Platform


def test_instagram_url_accepted_in_day09() -> None:
    info = validate_profile_url("https://www.instagram.com/natgeo")
    assert info.platform == Platform.INSTAGRAM
    assert info.handle == "natgeo"


def test_tiktok_url_accepted_in_day09() -> None:
    info = validate_profile_url("https://www.tiktok.com/@creator")
    assert info.platform == Platform.TIKTOK
    assert info.handle == "@creator"


def test_linkedin_url_rejected() -> None:
    with pytest.raises(UnsupportedPlatformError, match="LinkedIn live collection adapter is not yet configured"):
        validate_profile_url("https://www.linkedin.com/in/satyanadella")
