"""Granular unit test 34 for X adapter edge handling."""

from __future__ import annotations

from sbh.adapters.x import XAdapter
from sbh.contracts.platforms import Platform


def test_x_granular_check_34() -> None:
    adapter = XAdapter()
    assert adapter.platform == Platform.X
    assert "followers" in adapter.rate_limiters
    assert adapter.rate_limiters["followers"].limit == 15
