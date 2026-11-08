"""Tests for MockYouTubeClient fixture loader."""

from __future__ import annotations

from sbh.adapters.youtube_client import MockYouTubeClient


def test_mock_youtube_client_get_channel_success() -> None:
    client = MockYouTubeClient()
    data = client.get_channel("UCYO_jab_esuFRV4b17AJtAw")
    assert len(data.get("items", [])) == 1
    assert data["items"][0]["snippet"]["title"] == "3Blue1Brown"
    assert len(client.call_history) == 1


def test_mock_youtube_client_get_channel_not_found() -> None:
    client = MockYouTubeClient()
    data = client.get_channel("nonexistent")
    assert len(data.get("items", [])) == 0


def test_mock_youtube_client_playlist_items() -> None:
    client = MockYouTubeClient()
    data = client.list_playlist_items("UUYO_jab_esuFRV4b17AJtAw")
    assert len(data.get("items", [])) == 2
    assert data["items"][0]["snippet"]["title"].startswith("Fourier")
