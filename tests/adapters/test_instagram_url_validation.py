from __future__ import annotations

import pytest

from sbh.adapters.errors import InvalidUrlError
from sbh.adapters.url_validator import UrlType, validate_profile_url
from sbh.contracts.platforms import Platform


def test_validate_instagram_url_variants() -> None:
    cases = [
        ("https://www.instagram.com/creator_brand/", "creator_brand", True),
        ("https://instagram.com/creator_brand", "creator_brand", True),
        ("@creator_brand", "creator_brand", True),
        ("http://instagram.com/creator_brand?utm_source=feed", "creator_brand", False),
    ]
    for raw_url, expected_handle, expected_canonical in cases:
        info = validate_profile_url(raw_url, platform_hint=Platform.INSTAGRAM)
        assert info.platform == Platform.INSTAGRAM
        assert info.handle == expected_handle
        assert info.canonical_url == f"https://www.instagram.com/{expected_handle}"
        assert info.is_canonical == expected_canonical


def test_validate_instagram_autodetection() -> None:
    info = validate_profile_url("https://www.instagram.com/nature.photography")
    assert info.platform == Platform.INSTAGRAM
    assert info.handle == "nature.photography"
    assert info.url_type == UrlType.HANDLE


def test_validate_instagram_reserved_and_invalid() -> None:
    with pytest.raises(InvalidUrlError, match="reserved"):
        validate_profile_url("https://www.instagram.com/explore")

    with pytest.raises(InvalidUrlError, match="Invalid Instagram username"):
        validate_profile_url("https://www.instagram.com/.invalid.")

    with pytest.raises(InvalidUrlError, match="post or reel link"):
        validate_profile_url("https://www.instagram.com/p/DB12345/")
