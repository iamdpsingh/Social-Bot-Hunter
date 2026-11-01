"""Account storage protocol."""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any, Protocol, runtime_checkable


@runtime_checkable
class AccountStoreProtocol(Protocol):
    """Protocol defining account profile persistence and retrieval."""

    def upsert_account(self, record: Mapping[str, Any]) -> None:
        """Upsert a canonical account profile record."""
        ...

    def get_account(self, platform: str, account_id: str) -> Mapping[str, Any] | None:
        """Fetch account record by platform and identifier."""
        ...

    def list_accounts(self, *, limit: int = 100, offset: int = 0) -> list[Mapping[str, Any]]:
        """List stored accounts with pagination."""
        ...
