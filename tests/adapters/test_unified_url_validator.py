"""Tests for unified validate_profile_url entrypoint."""

from __future__ import annotations

import pytest
from sbh.adapters.errors import InvalidUrlError, UnsupportedPlatformError
from sbh.adapters.url_validator import validate_profile_url
from sbh.contracts.platforms import Platform


def test_autodetect_youtube_channel_url() -> None:
    res = validate_profile_url("https://www.youtube.com/@3blue1brown")
    assert res.platform == Platform.YOUTUBE
    assert res.handle == "@3blue1brown"


def test_autodetect_x_profile_url() -> None:
    res = validate_profile_url("https://x.com/satyanadella")
    assert res.platform == Platform.X
    assert res.handle == "satyanadella"


def test_platform_hint_override() -> None:
    res = validate_profile_url("@techlead", platform_hint=Platform.YOUTUBE)
    assert res.platform == Platform.YOUTUBE
    assert res.handle == "@techlead"


def test_empty_url_rejected() -> None:
    with pytest.raises(InvalidUrlError, match="cannot be empty"):
        validate_profile_url("   ")


def test_unknown_domain_rejected() -> None:
    with pytest.raises(UnsupportedPlatformError):
        validate_profile_url("https://mastodon.social/@someone")
