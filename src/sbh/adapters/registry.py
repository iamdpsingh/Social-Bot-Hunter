"""Factory and registry for platform adapters."""

from __future__ import annotations

from sbh.adapters.x import XAdapter
from sbh.adapters.youtube import YouTubeAdapter
from sbh.contracts.adapter import NotConfiguredAdapter, PlatformAdapter
from sbh.contracts.platforms import Platform


class AdapterRegistry:
    """Resolves and instantiates appropriate PlatformAdapter for a requested platform."""

    def __init__(self) -> None:
        self._custom_adapters: dict[Platform, PlatformAdapter] = {}
        # Default singletons
        self._youtube_adapter = YouTubeAdapter()
        self._x_adapter = XAdapter()

    def register(self, platform: Platform, adapter: PlatformAdapter) -> None:
        """Register a custom or mock adapter for a platform."""
        self._custom_adapters[platform] = adapter

    def get_adapter(self, platform: Platform) -> PlatformAdapter:
        """Return the active adapter for the given platform."""
        if platform in self._custom_adapters:
            return self._custom_adapters[platform]

        if platform == Platform.YOUTUBE:
            return self._youtube_adapter
        elif platform == Platform.X:
            return self._x_adapter
        else:
            return NotConfiguredAdapter(platform)


default_registry = AdapterRegistry()
