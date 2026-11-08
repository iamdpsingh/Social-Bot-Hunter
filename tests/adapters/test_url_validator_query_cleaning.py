"""Tests for query parameter stripping in URL validator."""

from __future__ import annotations

from sbh.adapters.url_validator import validate_profile_url


def test_strip_complex_utm_params() -> None:
    url = "https://x.com/satyanadella?utm_source=twitter&utm_medium=social&utm_campaign=share"
    info = validate_profile_url(url)
    assert info.canonical_url == "https://x.com/satyanadella"
    assert not info.is_canonical
