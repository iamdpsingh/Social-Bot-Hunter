"""Tests for unsupported platform rejection in URL validation."""

from __future__ import annotations

import pytest

from sbh.adapters.errors import UnsupportedPlatformError
from sbh.adapters.url_validator import validate_profile_url
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
