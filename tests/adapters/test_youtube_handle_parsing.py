"""Tests for YouTube @handle URL normalization."""

from __future__ import annotations

import pytest

from sbh.adapters.errors import InvalidUrlError
from sbh.adapters.url_validator import UrlType, _parse_youtube_url
from sbh.contracts.platforms import Platform


def test_youtube_bare_handle() -> None:
    res = _parse_youtube_url("@veritasium")
    assert res.platform == Platform.YOUTUBE
    assert res.handle == "@veritasium"
    assert res.canonical_url == "https://www.youtube.com/@veritasium"
    assert res.url_type == UrlType.HANDLE
    assert res.is_canonical


def test_youtube_full_url_handle() -> None:
    res = _parse_youtube_url("https://www.youtube.com/@mkbhd")
    assert res.handle == "@mkbhd"
    assert res.canonical_url == "https://www.youtube.com/@mkbhd"
    assert res.is_canonical


def test_youtube_url_with_query_params() -> None:
    res = _parse_youtube_url("https://youtube.com/@techlead?sub_confirmation=1")
    assert res.handle == "@techlead"
    assert res.canonical_url == "https://www.youtube.com/@techlead"
    assert not res.is_canonical


def test_youtube_invalid_handle_syntax() -> None:
    with pytest.raises(InvalidUrlError):
        _parse_youtube_url("@ab")  # Too short (< 3)
