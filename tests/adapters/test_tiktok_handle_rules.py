from __future__ import annotations

import pytest

from sbh.adapters.errors import InvalidUrlError
from sbh.adapters.url_validator import validate_profile_url
from sbh.contracts.platforms import Platform


def test_tiktok_valid_handles() -> None:
    valid = ["@dance_creator", "@valid.user", "@user_2026", "@trend_setter"]
    for h in valid:
        info = validate_profile_url(f"https://www.tiktok.com/{h}")
        assert info.platform == Platform.TIKTOK
        assert info.handle == h


def test_tiktok_reject_too_short() -> None:
    with pytest.raises(InvalidUrlError, match="Invalid TikTok username"):
        validate_profile_url("https://www.tiktok.com/@a")


def test_tiktok_reject_too_long() -> None:
    too_long = "@" + "a" * 25
    with pytest.raises(InvalidUrlError, match="Invalid TikTok username"):
        validate_profile_url(f"https://www.tiktok.com/{too_long}")


def test_tiktok_reject_consecutive_dots() -> None:
    with pytest.raises(InvalidUrlError, match="Invalid TikTok username"):
        validate_profile_url("https://www.tiktok.com/@bad..handle")
