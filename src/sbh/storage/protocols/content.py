"""Content item storage protocol."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from typing import Any, Protocol, runtime_checkable


@runtime_checkable
class ContentStoreProtocol(Protocol):
    """Protocol defining content item ingestion and retrieval."""

    def insert_content_batch(self, items: Sequence[Mapping[str, Any]]) -> int:
        """Batch insert content items."""
        ...

    def get_account_content(
        self, platform: str, account_id: str, *, limit: int = 100
    ) -> list[Mapping[str, Any]]:
        """Fetch chronological content for an account."""
        ...
