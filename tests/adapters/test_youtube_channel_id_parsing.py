"""Tests for YouTube 24-character canonical channel ID parsing."""

from __future__ import annotations

import pytest

from sbh.adapters.errors import InvalidUrlError
from sbh.adapters.url_validator import UrlType, _parse_youtube_url
from sbh.contracts.platforms import Platform

VALID_CHANNEL_ID = "UC_x5XG1OV2P6uZZ5FSM9Ttw"


def test_youtube_bare_channel_id() -> None:
    res = _parse_youtube_url(VALID_CHANNEL_ID)
    assert res.platform == Platform.YOUTUBE
    assert res.handle == VALID_CHANNEL_ID
    assert res.channel_id == VALID_CHANNEL_ID
    assert res.canonical_url == f"https://www.youtube.com/channel/{VALID_CHANNEL_ID}"
    assert res.url_type == UrlType.CHANNEL_ID
    assert res.is_canonical


def test_youtube_channel_url() -> None:
    res = _parse_youtube_url(f"https://www.youtube.com/channel/{VALID_CHANNEL_ID}")
    assert res.channel_id == VALID_CHANNEL_ID
    assert res.is_canonical


def test_youtube_channel_url_with_tab() -> None:
    res = _parse_youtube_url(f"https://youtube.com/channel/{VALID_CHANNEL_ID}/videos")
    assert res.channel_id == VALID_CHANNEL_ID
    assert not res.is_canonical
    assert res.canonical_url == f"https://www.youtube.com/channel/{VALID_CHANNEL_ID}"


def test_youtube_invalid_channel_id_length() -> None:
    with pytest.raises(InvalidUrlError, match="Invalid YouTube 24-character channel ID"):
        _parse_youtube_url("https://www.youtube.com/channel/UCshort")
