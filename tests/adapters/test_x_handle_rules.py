"""Tests for X handle constraints and format rules."""

from __future__ import annotations

import pytest

from sbh.adapters.errors import InvalidUrlError
from sbh.adapters.url_validator import _parse_x_url
from sbh.contracts.platforms import Platform


def test_valid_x_handles() -> None:
    res = _parse_x_url("@elonmusk")
    assert res.platform == Platform.X
    assert res.handle == "elonmusk"
    assert res.canonical_url == "https://x.com/elonmusk"
    assert res.is_canonical


def test_x_handle_with_underscores_and_numbers() -> None:
    res = _parse_x_url("@user_123_abc")
    assert res.handle == "user_123_abc"


def test_x_handle_too_long() -> None:
    with pytest.raises(InvalidUrlError, match="must be 1-15 alphanumeric characters"):
        _parse_x_url("@username_is_way_too_long_for_x")


def test_x_handle_illegal_characters() -> None:
    with pytest.raises(InvalidUrlError, match="must be 1-15 alphanumeric characters"):
        _parse_x_url("@user$name!")
