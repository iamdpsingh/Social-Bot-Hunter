"""Connection pool protocol."""

from __future__ import annotations

from typing import Any, Mapping, Protocol, runtime_checkable


@runtime_checkable
class ConnectionPoolProtocol(Protocol):
    """Protocol defining connection pool lifecycle and statistics."""

    def get_connection(self, *, timeout: float = 30.0) -> Any:
        """Acquire connection from pool."""
        ...

    def release_connection(self, conn: Any) -> None:
        """Return connection to pool."""
        ...

    def stats(self) -> Mapping[str, int]:
        """Return allocated, idle, and waiting connection counts."""
        ...
