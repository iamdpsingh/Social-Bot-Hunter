"""Base protocol for storage repositories."""

from __future__ import annotations

from typing import Protocol, runtime_checkable


@runtime_checkable
class BaseRepositoryProtocol(Protocol):
    """Protocol defining the core database repository lifecycle contract."""

    def close(self) -> None:
        """Close any allocated connection resources."""
        ...
