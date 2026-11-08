"""Granular unit test 17 for YouTube adapter edge handling."""

from __future__ import annotations

from sbh.adapters.youtube import YouTubeAdapter
from sbh.contracts.platforms import Platform


def test_youtube_granular_check_17() -> None:
    adapter = YouTubeAdapter()
    assert adapter.platform == Platform.YOUTUBE
    assert adapter.quota_tracker.daily_limit == 10000
    assert adapter._channel_id_to_upload_playlist_id("UC1234567890123456789012") == "UU1234567890123456789012"
