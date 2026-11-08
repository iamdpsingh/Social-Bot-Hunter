"""Tests for X URL canonicalization and parameter stripping."""

from __future__ import annotations

from sbh.adapters.url_validator import UrlType, _parse_x_url


def test_twitter_domain_canonicalized_to_x() -> None:
    res = _parse_x_url("https://twitter.com/support")
    assert res.handle == "support"
    assert res.canonical_url == "https://x.com/support"
    assert not res.is_canonical  # twitter.com -> x.com


def test_strip_tracking_parameters() -> None:
    res = _parse_x_url("https://x.com/jack?s=20&t=xyz789")
    assert res.handle == "jack"
    assert res.canonical_url == "https://x.com/jack"
    assert not res.is_canonical


def test_extract_handle_from_tweet_status_permalink() -> None:
    res = _parse_x_url("https://x.com/barackobama/status/1234567890123456789")
    assert res.handle == "barackobama"
    assert res.canonical_url == "https://x.com/barackobama"
    assert res.url_type == UrlType.STATUS_LINK
    assert not res.is_canonical
