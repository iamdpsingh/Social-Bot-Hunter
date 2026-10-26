"""Platform capability registry.

The registry records what each platform integration can do *and how far that claim has
been verified*. It never asserts endpoints, scopes or approval requirements that nobody
has checked against current official documentation: those fields stay empty and the
status stays ``not_configured`` until a human researches them (Phase 5/6).
"""

from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass, field
from datetime import datetime
from enum import StrEnum

from sbh.contracts.platforms import Platform


class Operation(StrEnum):
    DATASET_IMPORT = "dataset_import"
    LOOKUP_ACCOUNT = "lookup_account"
    LIST_FOLLOWERS = "list_followers"
    LIST_FOLLOWING = "list_following"
    LIST_CONTENT = "list_content"


class CollectionMode(StrEnum):
    OFFICIAL_API = "official_api"
    DATASET_IMPORT = "dataset_import"
    PUBLIC_DATA = "public_data"


class CapabilityStatus(StrEnum):
    IMPLEMENTED = "implemented"
    VERIFIED = "verified"
    REQUIRES_APPROVAL = "requires_approval"
    UNSUPPORTED = "unsupported"
    TEMPORARILY_UNAVAILABLE = "temporarily_unavailable"
    NOT_CONFIGURED = "not_configured"


@dataclass(frozen=True)
class Capability:
    platform: Platform
    operation: Operation
    status: CapabilityStatus
    mode: CollectionMode
    # None means "not yet established from official documentation", which is different
    # from False ("documented as unsupported").
    supported: bool | None = None
    endpoint: str | None = None
    api_version: str | None = None
    required_scopes: tuple[str, ...] = ()
    requires_approval: bool | None = None
    pagination_notes: str | None = None
    quota_notes: str | None = None
    credentials_required: tuple[str, ...] = ()
    retention_notes: str | None = None
    limitations: tuple[str, ...] = field(default_factory=tuple)
    last_verified_at: datetime | None = None
    verification_evidence: str | None = None

    def __post_init__(self) -> None:
        if self.status is CapabilityStatus.VERIFIED:
            if self.last_verified_at is None or not self.verification_evidence:
                raise ValueError(
                    "status 'verified' requires last_verified_at and verification_evidence "
                    "(a real integration test against an authorised environment)"
                )
            if self.supported is not True:
                raise ValueError("status 'verified' requires supported=True")
        if self.status is CapabilityStatus.UNSUPPORTED and self.supported is True:
            raise ValueError("status 'unsupported' contradicts supported=True")
        if (
            self.mode is CollectionMode.OFFICIAL_API
            and self.status in (CapabilityStatus.IMPLEMENTED, CapabilityStatus.VERIFIED)
            and not (self.endpoint and self.api_version)
        ):
            raise ValueError(
                "an implemented official-API operation must document its endpoint and API version"
            )


class CapabilityRegistry:
    def __init__(self, capabilities: Iterable[Capability]) -> None:
        self._by_key: dict[tuple[Platform, Operation], Capability] = {}
        for cap in capabilities:
            key = (cap.platform, cap.operation)
            if key in self._by_key:
                raise ValueError(f"duplicate capability for {key}")
            self._by_key[key] = cap

    def get(self, platform: Platform, operation: Operation) -> Capability:
        try:
            return self._by_key[(platform, operation)]
        except KeyError:
            raise KeyError(f"no capability registered for {platform.value}/{operation.value}") from None

    def all(self) -> list[Capability]:
        return sorted(self._by_key.values(), key=lambda c: (c.platform.value, c.operation.value))

    def for_platform(self, platform: Platform) -> list[Capability]:
        return [c for c in self.all() if c.platform is platform]

    def can_collect(self, platform: Platform, operation: Operation) -> tuple[bool, str]:
        """Decide whether an operation may be attempted, and say why not if it cannot."""
        cap = self.get(platform, operation)
        if cap.status in (CapabilityStatus.IMPLEMENTED, CapabilityStatus.VERIFIED):
            return True, cap.status.value
        return False, f"{platform.value}/{operation.value} is {cap.status.value}: " + (
            "; ".join(cap.limitations) or "no further detail recorded"
        )


_LIVE_OPERATIONS = (
    Operation.LOOKUP_ACCOUNT,
    Operation.LIST_FOLLOWERS,
    Operation.LIST_FOLLOWING,
    Operation.LIST_CONTENT,
)

_NOT_RESEARCHED = (
    "No adapter is implemented.",
    "Endpoint availability, permissions, approval requirements and quotas have not been "
    "researched against current official platform documentation.",
)

_DATASET_LIMITATIONS = (
    "Relationship completeness is only as good as the coverage declared in the dataset manifest.",
    "The importer is responsible for the dataset's provenance and permitted use.",
)


def default_registry() -> CapabilityRegistry:
    caps: list[Capability] = []
    for platform in Platform:
        caps.append(
            Capability(
                platform=platform,
                operation=Operation.DATASET_IMPORT,
                status=CapabilityStatus.IMPLEMENTED,
                mode=CollectionMode.DATASET_IMPORT,
                supported=True,
                limitations=_DATASET_LIMITATIONS,
            )
        )
        for op in _LIVE_OPERATIONS:
            caps.append(
                Capability(
                    platform=platform,
                    operation=op,
                    status=CapabilityStatus.NOT_CONFIGURED,
                    mode=CollectionMode.OFFICIAL_API,
                    supported=None,
                    limitations=_NOT_RESEARCHED,
                )
            )
    return CapabilityRegistry(caps)


def registry_markdown(registry: CapabilityRegistry) -> str:
    """Render the registry as a Markdown table (embedded in docs/platform-access-matrix.md)."""
    rows = [
        "| Platform | Operation | Mode | Status | Supported | Endpoint / version | Verified |",
        "|---|---|---|---|---|---|---|",
    ]
    for c in registry.all():
        supported = {True: "yes", False: "no", None: "unknown"}[c.supported]
        endpoint = f"{c.endpoint} ({c.api_version})" if c.endpoint else "-"
        verified = c.last_verified_at.date().isoformat() if c.last_verified_at else "never"
        rows.append(
            f"| {c.platform.value} | {c.operation.value} | {c.mode.value} | {c.status.value} "
            f"| {supported} | {endpoint} | {verified} |"
        )
    return "\n".join(rows)
