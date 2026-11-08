"""Tests for rejection of YouTube video links in channel probe."""

from __future__ import annotations

import pytest

from sbh.adapters.errors import InvalidUrlError
from sbh.adapters.url_validator import _parse_youtube_url


@pytest.mark.parametrize(
    "video_link",
    [
        "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
        "https://youtu.be/dQw4w9WgXcQ",
        "https://www.youtube.com/shorts/3xyz987",
    ],
)
def test_youtube_video_links_rejected(video_link: str) -> None:
    with pytest.raises(InvalidUrlError, match="Expected a YouTube channel or profile URL"):
        _parse_youtube_url(video_link)
