"""Ingestion checkpoint storage protocol."""

from __future__ import annotations

from typing import Any, Mapping, Protocol, runtime_checkable


@runtime_checkable
class CheckpointStoreProtocol(Protocol):
    """Protocol defining ingestion pagination checkpoint persistence."""

    def save_checkpoint(self, scan_id: str, platform: str, cursor: str, state: Mapping[str, Any]) -> None:
        """Save stream pagination checkpoint."""
        ...

    def get_checkpoint(self, scan_id: str, platform: str) -> Mapping[str, Any] | None:
        """Retrieve stored stream checkpoint."""
        ...
