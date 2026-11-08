"""Tests for rejection of reserved X routes."""

from __future__ import annotations

import pytest

from sbh.adapters.errors import InvalidUrlError
from sbh.adapters.url_validator import _parse_x_url


@pytest.mark.parametrize(
    "reserved",
    [
        "home",
        "explore",
        "notifications",
        "messages",
        "settings",
        "search",
        "about",
    ],
)
def test_reserved_x_paths_rejected(reserved: str) -> None:
    with pytest.raises(InvalidUrlError, match="reserved X system route"):
        _parse_x_url(f"https://x.com/{reserved}")
