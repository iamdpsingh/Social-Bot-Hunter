"""Tests for AdapterRegistry factory."""

from __future__ import annotations

from sbh.adapters.registry import AdapterRegistry
from sbh.adapters.x import XAdapter
from sbh.adapters.youtube import YouTubeAdapter
from sbh.contracts.adapter import NotConfiguredAdapter
from sbh.contracts.platforms import Platform


def test_registry_returns_youtube_adapter() -> None:
    reg = AdapterRegistry()
    adapter = reg.get_adapter(Platform.YOUTUBE)
    assert isinstance(adapter, YouTubeAdapter)


def test_registry_returns_x_adapter() -> None:
    reg = AdapterRegistry()
    adapter = reg.get_adapter(Platform.X)
    assert isinstance(adapter, XAdapter)


def test_registry_returns_not_configured_for_others() -> None:
    reg = AdapterRegistry()
    for p in (Platform.INSTAGRAM, Platform.TIKTOK, Platform.LINKEDIN):
        adapter = reg.get_adapter(p)
        assert isinstance(adapter, NotConfiguredAdapter)
