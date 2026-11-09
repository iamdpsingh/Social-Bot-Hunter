from __future__ import annotations

import pytest

from sbh.adapters.errors import InvalidUrlError
from sbh.adapters.url_validator import validate_profile_url
from sbh.contracts.platforms import Platform


def test_instagram_valid_handle_characters() -> None:
    valid_handles = [
        "user_name",
        "user.name",
        "user123",
        "u_s_e_r",
        "official.account.2026",
    ]
    for h in valid_handles:
        info = validate_profile_url(f"https://www.instagram.com/{h}")
        assert info.platform == Platform.INSTAGRAM
        assert info.handle == h


def test_instagram_reject_consecutive_dots() -> None:
    with pytest.raises(InvalidUrlError, match="Invalid Instagram username"):
        validate_profile_url("https://www.instagram.com/user..name")


def test_instagram_reject_leading_trailing_dots() -> None:
    with pytest.raises(InvalidUrlError, match="Invalid Instagram username"):
        validate_profile_url("https://www.instagram.com/.username")

    with pytest.raises(InvalidUrlError, match="Invalid Instagram username"):
        validate_profile_url("https://www.instagram.com/username.")


def test_instagram_reject_too_long() -> None:
    too_long = "a" * 31
    with pytest.raises(InvalidUrlError, match="Invalid Instagram username"):
        validate_profile_url(f"https://www.instagram.com/{too_long}")
