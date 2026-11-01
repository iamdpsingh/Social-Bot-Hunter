"""Community cluster storage protocol."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from typing import Any, Protocol, runtime_checkable


@runtime_checkable
class CommunityStoreProtocol(Protocol):
    """Protocol defining detected coordinated cluster persistence."""

    def save_communities(self, scan_id: str, clusters: Sequence[Mapping[str, Any]]) -> int:
        """Save detected community clusters for a scan."""
        ...

    def get_communities(self, scan_id: str) -> list[Mapping[str, Any]]:
        """Retrieve all detected communities for a scan."""
        ...
