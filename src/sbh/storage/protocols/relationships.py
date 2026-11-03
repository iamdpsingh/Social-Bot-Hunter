"""Relationship graph storage protocol."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from typing import Any, Protocol, runtime_checkable


@runtime_checkable
class RelationshipStoreProtocol(Protocol):
    """Protocol defining relationship graph edge persistence and queries."""

    def insert_relationships_batch(self, edges: Sequence[Mapping[str, Any]]) -> int:
        """Batch insert relationship edges."""
        ...

    def list_relationships(
        self, *, platform: str, limit: int = 500, offset: int = 0
    ) -> list[Mapping[str, Any]]:
        """List relationship edges for a platform."""
        ...

    def get_neighborhood(
        self, platform: str, account_id: str, *, depth: int = 1
    ) -> Sequence[Mapping[str, Any]]:
        """Get k-hop neighborhood for a specified account."""
        ...
