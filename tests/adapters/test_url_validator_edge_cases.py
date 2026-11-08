"""Tests for edge cases in profile URL parsing."""

from __future__ import annotations

from sbh.adapters.url_validator import validate_profile_url


def test_url_with_whitespace_and_tabs() -> None:
    res = validate_profile_url("  \thttps://x.com/karpathy\n  ")
    assert res.handle == "karpathy"


def test_url_with_trailing_slashes() -> None:
    res = validate_profile_url("https://x.com/ylecun////")
    assert res.handle == "ylecun"
    assert res.canonical_url == "https://x.com/ylecun"


def test_url_case_insensitivity() -> None:
    res = validate_profile_url("https://X.COM/GeoffreyHinton")
    assert res.handle == "geoffreyhinton"
    assert res.canonical_url == "https://x.com/geoffreyhinton"
