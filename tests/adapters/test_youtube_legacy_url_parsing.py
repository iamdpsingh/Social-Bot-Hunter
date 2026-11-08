"""Tests for legacy /c/ and /user/ YouTube profile paths."""

from __future__ import annotations

from sbh.adapters.url_validator import UrlType, _parse_youtube_url


def test_youtube_custom_c_url() -> None:
    res = _parse_youtube_url("https://www.youtube.com/c/CreatorStudio")
    assert res.handle == "CreatorStudio"
    assert res.canonical_url == "https://www.youtube.com/c/CreatorStudio"
    assert res.url_type == UrlType.CUSTOM_URL
    assert not res.is_canonical


def test_youtube_legacy_user_url() -> None:
    res = _parse_youtube_url("https://www.youtube.com/user/oldchannelname")
    assert res.handle == "oldchannelname"
    assert res.canonical_url == "https://www.youtube.com/user/oldchannelname"
    assert res.url_type == UrlType.LEGACY_USER
    assert not res.is_canonical
