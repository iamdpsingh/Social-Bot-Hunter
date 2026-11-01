"""Investigation report storage protocol."""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any, Protocol, runtime_checkable


@runtime_checkable
class ReportStoreProtocol(Protocol):
    """Protocol defining investigation report persistence."""

    def save_report(self, scan_id: str, report_data: Mapping[str, Any]) -> None:
        """Save synthesized investigation report."""
        ...

    def get_report(self, scan_id: str) -> Mapping[str, Any] | None:
        """Retrieve stored investigation report."""
        ...
