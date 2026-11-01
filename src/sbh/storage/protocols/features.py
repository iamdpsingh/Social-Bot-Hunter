"""Feature store protocol."""

from __future__ import annotations

from typing import Any, Mapping, Protocol, Sequence, runtime_checkable


@runtime_checkable
class FeatureStoreProtocol(Protocol):
    """Protocol defining calculated feature storage and retrieval."""

    def save_features(self, scan_id: str, features: Sequence[Mapping[str, Any]]) -> int:
        """Save computed account feature vectors for a scan."""
        ...

    def get_features(self, scan_id: str, account_id: str) -> Mapping[str, Any] | None:
        """Retrieve computed feature vector for an account."""
        ...
