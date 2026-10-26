"""Platform adapter contract.

Every live integration implements ``PlatformAdapter``. Adapters return the same record
types as the dataset importer, so live and imported data share one normalisation,
validation and storage path. Access denial, missing approval and unsupported operations
are explicit ``AccessOutcome`` values, never empty successes.
"""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass, field
from enum import StrEnum
from typing import Generic, Protocol, TypeVar

from sbh.contracts.capabilities import Capability, CapabilityStatus, Operation
from sbh.contracts.platforms import Platform
from sbh.schemas.records import (
    AccountObservationRecord,
    ContentRecord,
    ListKind,
    RelationshipRecord,
)

T = TypeVar("T")


class AccessOutcome(StrEnum):
    OK = "ok"
    DENIED = "denied"
    UNSUPPORTED = "unsupported"
    NOT_CONFIGURED = "not_configured"
    REQUIRES_APPROVAL = "requires_approval"
    RATE_LIMITED = "rate_limited"
    UNAVAILABLE = "unavailable"


@dataclass(frozen=True)
class Page(Generic[T]):
    """One page of adapter results.

    ``items`` empty with ``outcome == OK`` and ``next_cursor is None`` means the list is
    genuinely exhausted. Any other outcome means the data is *unavailable*, not empty.
    """

    outcome: AccessOutcome
    items: Sequence[T] = field(default_factory=tuple)
    next_cursor: str | None = None
    limitation: str | None = None
    retry_after_seconds: float | None = None


class PlatformAdapter(Protocol):
    platform: Platform

    def capabilities(self) -> list[Capability]: ...

    def lookup_account(self, platform_account_id: str) -> Page[AccountObservationRecord]: ...

    def list_relationships(
        self, platform_account_id: str, kind: ListKind, cursor: str | None = None
    ) -> Page[RelationshipRecord]: ...

    def list_content(
        self, platform_account_id: str, cursor: str | None = None
    ) -> Page[ContentRecord]: ...


class NotConfiguredAdapter:
    """Placeholder that reports honestly that no live integration exists.

    It exists so the rest of the system has a concrete object to call; it never returns
    fabricated data.
    """

    def __init__(self, platform: Platform) -> None:
        self.platform = platform

    def capabilities(self) -> list[Capability]:
        from sbh.contracts.capabilities import CollectionMode

        return [
            Capability(
                platform=self.platform,
                operation=op,
                status=CapabilityStatus.NOT_CONFIGURED,
                mode=CollectionMode.OFFICIAL_API,
                supported=None,
                limitations=("No adapter is implemented.",),
            )
            for op in (
                Operation.LOOKUP_ACCOUNT,
                Operation.LIST_FOLLOWERS,
                Operation.LIST_FOLLOWING,
                Operation.LIST_CONTENT,
            )
        ]

    def _page(self, what: str) -> Page[T]:  # type: ignore[type-var]
        return Page(
            outcome=AccessOutcome.NOT_CONFIGURED,
            limitation=f"{self.platform.value}: {what} is not configured (no adapter implemented).",
        )

    def lookup_account(self, platform_account_id: str) -> Page[AccountObservationRecord]:
        return self._page("account lookup")

    def list_relationships(
        self, platform_account_id: str, kind: ListKind, cursor: str | None = None
    ) -> Page[RelationshipRecord]:
        return self._page(f"{kind.value} listing")

    def list_content(
        self, platform_account_id: str, cursor: str | None = None
    ) -> Page[ContentRecord]:
        return self._page("content listing")
