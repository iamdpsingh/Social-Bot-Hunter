"""Tests for Bluesky handle and DID validation."""

from __future__ import annotations

from sbh.adapters.url_validator import UrlType, _parse_bluesky_url
from sbh.contracts.platforms import Platform


def test_bluesky_handle_url() -> None:
    res = _parse_bluesky_url("https://bsky.app/profile/alice.bsky.social")
    assert res.platform == Platform.BLUESKY
    assert res.handle == "alice.bsky.social"
    assert res.canonical_url == "https://bsky.app/profile/alice.bsky.social"
    assert res.url_type == UrlType.HANDLE
    assert res.is_canonical


def test_bluesky_did_url() -> None:
    did = "did:plc:z72i7hdynmk6r22z27h6tvur"
    res = _parse_bluesky_url(f"https://bsky.app/profile/{did}")
    assert res.handle == did
    assert res.url_type == UrlType.DID


def test_bluesky_bare_did() -> None:
    did = "did:plc:z72i7hdynmk6r22z27h6tvur"
    res = _parse_bluesky_url(did)
    assert res.handle == did
    assert res.url_type == UrlType.DID
