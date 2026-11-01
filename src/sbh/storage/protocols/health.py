"""Storage health check protocol."""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any, Protocol, runtime_checkable


@runtime_checkable
class StorageHealthProtocol(Protocol):
    """Protocol defining database health and latency probes."""

    def ping(self) -> float:
        """Execute lightweight query and return round-trip latency in ms."""
        ...

    def pool_status(self) -> Mapping[str, Any]:
        """Return connection pool status and connection metrics."""
        ...
