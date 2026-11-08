"""Tests for MockXClient fixture replay."""

from __future__ import annotations

from sbh.adapters.x_client import MockXClient


def test_mock_x_client_lookup_user() -> None:
    client = MockXClient()
    data = client.get_user_by_username("elonmusk")
    assert "data" in data
    assert data["data"]["username"] == "elonmusk"
    assert data["data"]["public_metrics"]["followers_count"] == 195000000


def test_mock_x_client_lookup_user_not_found() -> None:
    client = MockXClient()
    data = client.get_user_by_username("nonexistent")
    assert "errors" in data
    assert data["errors"][0]["title"] == "Not Found Error"


def test_mock_x_client_followers_pagination() -> None:
    client = MockXClient()
    p1 = client.list_followers("44196397")
    assert len(p1["data"]) == 2
    assert p1["meta"]["next_token"] == "token_page_2"

    p2 = client.list_followers("44196397", pagination_token="token_page_2")
    assert len(p2["data"]) == 1
    assert "next_token" not in p2["meta"]
