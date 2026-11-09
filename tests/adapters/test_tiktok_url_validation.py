from __future__ import annotations

import pytest

from sbh.adapters.errors import InvalidUrlError
from sbh.adapters.url_validator import UrlType, validate_profile_url
from sbh.contracts.platforms import Platform


def test_validate_tiktok_url_variants() -> None:
    cases = [
        ("https://www.tiktok.com/@dance_creator", "@dance_creator", True),
        ("https://tiktok.com/@dance_creator", "@dance_creator", True),
        ("@dance_creator", "@dance_creator", True),
        ("https://www.tiktok.com/@dance_creator?lang=en", "@dance_creator", False),
    ]
    for raw_url, expected_handle, expected_canonical in cases:
        info = validate_profile_url(raw_url, platform_hint=Platform.TIKTOK)
        assert info.platform == Platform.TIKTOK
        assert info.handle == expected_handle
        assert info.canonical_url == f"https://www.tiktok.com/{expected_handle}"
        assert info.is_canonical == expected_canonical


def test_validate_tiktok_autodetection() -> None:
    info = validate_profile_url("https://www.tiktok.com/@tech_reviewer")
    assert info.platform == Platform.TIKTOK
    assert info.handle == "@tech_reviewer"
    assert info.url_type == UrlType.HANDLE


def test_validate_tiktok_reserved_and_invalid() -> None:
    with pytest.raises(InvalidUrlError, match="reserved"):
        validate_profile_url("https://www.tiktok.com/@foryou")

    with pytest.raises(InvalidUrlError, match="Invalid TikTok username"):
        validate_profile_url("https://www.tiktok.com/@a")

    with pytest.raises(InvalidUrlError, match="video watch link"):
        validate_profile_url("https://www.tiktok.com/@user/video/710000000001")
