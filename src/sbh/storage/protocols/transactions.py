"""Transaction and savepoint management protocol."""

from __future__ import annotations

from typing import Protocol, runtime_checkable


@runtime_checkable
class TransactionProtocol(Protocol):
    """Protocol defining explicit database transaction boundaries."""

    def begin(self) -> None:
        """Begin transaction."""
        ...

    def commit(self) -> None:
        """Commit transaction."""
        ...

    def rollback(self) -> None:
        """Rollback transaction."""
        ...

    def create_savepoint(self, name: str) -> None:
        """Create named savepoint."""
        ...

    def rollback_savepoint(self, name: str) -> None:
        """Rollback to named savepoint."""
        ...
