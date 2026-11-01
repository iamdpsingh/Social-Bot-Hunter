"""Scan lifecycle storage protocol."""

from __future__ import annotations

from typing import Any, Mapping, Protocol, runtime_checkable


@runtime_checkable
class ScanStoreProtocol(Protocol):
    """Protocol defining investigation scan job lifecycle operations."""

    def create_scan(self, scan_id: str, platform: str, target: str, scope: str) -> Mapping[str, Any]:
        """Create and queue a new investigation scan."""
        ...

    def update_status(self, scan_id: str, status: str, *, error: str | None = None) -> None:
        """Update scan execution status."""
        ...

    def get_scan(self, scan_id: str) -> Mapping[str, Any] | None:
        """Get scan record by unique identifier."""
        ...

    def list_scans(self, *, limit: int = 50, offset: int = 0) -> list[Mapping[str, Any]]:
        """List investigation scans with pagination."""
        ...
