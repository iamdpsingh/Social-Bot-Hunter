"""Quarantine dead-letter storage protocol."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from typing import Any, Protocol, runtime_checkable


@runtime_checkable
class QuarantineStoreProtocol(Protocol):
    """Protocol defining malformed data dead-letter quarantine operations."""

    def quarantine_records(self, batch_id: str, violations: Sequence[Mapping[str, Any]]) -> int:
        """Write dead-letter records with violation reasons."""
        ...

    def list_quarantine(self, *, batch_id: str | None = None, limit: int = 100) -> list[Mapping[str, Any]]:
        """List quarantined records."""
        ...

    def get_quarantine_stats(self) -> Mapping[str, Any]:
        """Get aggregate quarantine summary statistics."""
        ...
