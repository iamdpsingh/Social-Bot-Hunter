"""Tests for ProfileUrlInfo dataclass properties."""

from __future__ import annotations

import pytest

from sbh.adapters.url_validator import ProfileUrlInfo, UrlType
from sbh.contracts.platforms import Platform


def test_profile_url_info_creation() -> None:
    info = ProfileUrlInfo(
        platform=Platform.YOUTUBE,
        handle="techlead",
        canonical_url="https://youtube.com/@techlead",
        raw_url="https://www.youtube.com/@techlead?sub_confirmation=1",
        url_type=UrlType.HANDLE,
        is_canonical=False,
    )
    assert info.platform == Platform.YOUTUBE
    assert info.handle == "techlead"
    assert info.canonical_url == "https://youtube.com/@techlead"
    assert info.url_type == UrlType.HANDLE
    assert not info.is_canonical
    assert info.channel_id is None


def test_profile_url_info_immutability() -> None:
    info = ProfileUrlInfo(
        platform=Platform.X,
        handle="jack",
        canonical_url="https://x.com/jack",
        raw_url="https://x.com/jack",
        url_type=UrlType.HANDLE,
        is_canonical=True,
    )
    with pytest.raises(AttributeError):
        info.handle = "other"  # type: ignore[misc]
