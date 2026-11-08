"""Additional unit tests for URL validator coverage."""

from __future__ import annotations

import pytest

from sbh.adapters.errors import InvalidUrlError, UnsupportedPlatformError
from sbh.adapters.url_validator import validate_profile_url


def test_youtube_short_name_rejected() -> None:
    with pytest.raises(InvalidUrlError):
        validate_profile_url("https://www.youtube.com/@a")


def test_x_empty_path_rejected() -> None:
    with pytest.raises(InvalidUrlError, match="No username found in X URL"):
        validate_profile_url("https://x.com/")


def test_unknown_social_network_rejected() -> None:
    with pytest.raises(UnsupportedPlatformError):
        validate_profile_url("https://threads.net/@zuck")
