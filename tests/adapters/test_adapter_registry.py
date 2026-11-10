"""Tests for AdapterRegistry factory."""

from __future__ import annotations

from sbh.adapters.instagram import InstagramAdapter
from sbh.adapters.linkedin import LinkedInAdapter
from sbh.adapters.registry import AdapterRegistry
from sbh.adapters.tiktok import TikTokAdapter
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


def test_registry_returns_instagram_adapter() -> None:
    reg = AdapterRegistry()
    adapter = reg.get_adapter(Platform.INSTAGRAM)
    assert isinstance(adapter, InstagramAdapter)


def test_registry_returns_tiktok_adapter() -> None:
    reg = AdapterRegistry()
    adapter = reg.get_adapter(Platform.TIKTOK)
    assert isinstance(adapter, TikTokAdapter)


def test_registry_returns_linkedin_adapter() -> None:
    reg = AdapterRegistry()
    adapter = reg.get_adapter(Platform.LINKEDIN)
    assert isinstance(adapter, LinkedInAdapter)


def test_registry_returns_not_configured_for_others() -> None:
    reg = AdapterRegistry()
    adapter = reg.get_adapter("unknown")  # type: ignore[arg-type]
    assert isinstance(adapter, NotConfiguredAdapter)
