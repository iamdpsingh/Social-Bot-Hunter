from __future__ import annotations

from sbh.adapters.instagram import InstagramAdapter
from sbh.adapters.registry import default_registry
from sbh.adapters.tiktok import TikTokAdapter
from sbh.adapters.x import XAdapter
from sbh.adapters.youtube import YouTubeAdapter
from sbh.contracts.platforms import Platform


def test_registry_resolves_all_four_active_platforms() -> None:
    yt = default_registry.get_adapter(Platform.YOUTUBE)
    assert isinstance(yt, YouTubeAdapter)
    assert yt.platform == Platform.YOUTUBE

    x = default_registry.get_adapter(Platform.X)
    assert isinstance(x, XAdapter)
    assert x.platform == Platform.X

    ig = default_registry.get_adapter(Platform.INSTAGRAM)
    assert isinstance(ig, InstagramAdapter)
    assert ig.platform == Platform.INSTAGRAM

    tk = default_registry.get_adapter(Platform.TIKTOK)
    assert isinstance(tk, TikTokAdapter)
    assert tk.platform == Platform.TIKTOK


def test_registry_capabilities_non_empty() -> None:
    for plat in (Platform.YOUTUBE, Platform.X, Platform.INSTAGRAM, Platform.TIKTOK):
        adapter = default_registry.get_adapter(plat)
        caps = adapter.capabilities()
        assert len(caps) >= 3
