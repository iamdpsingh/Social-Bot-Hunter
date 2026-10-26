"""Record types for dataset import and adapter output.

Missing and zero are different: optional numeric/boolean fields are ``None`` when the
source did not supply them, and a real ``0`` or ``False`` otherwise.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from enum import StrEnum

SCHEMA_VERSION = "1.0"


class RelationshipType(StrEnum):
    FOLLOWS = "follows"  # source -> target; the reverse is never inferred


class ListKind(StrEnum):
    FOLLOWERS = "followers"
    FOLLOWING = "following"


class Completeness(StrEnum):
    COMPLETE = "complete"
    PARTIAL = "partial"
    UNKNOWN = "unknown"


class CollectionMethod(StrEnum):
    OFFICIAL_API_EXPORT = "official_api_export"
    PERMITTED_PUBLIC_COLLECTION = "permitted_public_collection"
    THIRD_PARTY_DATASET = "third_party_dataset"
    SYNTHETIC = "synthetic"


class VerificationStatus(StrEnum):
    UNVERIFIED = "unverified"
    SOURCE_ASSERTED = "source_asserted"
    CROSS_CHECKED = "cross_checked"


@dataclass(frozen=True)
class CoverageDeclaration:
    platform_account_id: str
    list_kind: ListKind
    completeness: Completeness
    expected_count: int | None = None


@dataclass(frozen=True)
class Manifest:
    schema_version: str
    dataset_name: str
    platform: str
    collected_at: datetime
    source_description: str
    collection_method: CollectionMethod
    coverage_default: Completeness
    coverage_overrides: tuple[CoverageDeclaration, ...] = ()
    notes: str | None = None

    @property
    def is_synthetic(self) -> bool:
        return self.collection_method is CollectionMethod.SYNTHETIC


@dataclass(frozen=True)
class AccountObservationRecord:
    platform: str
    platform_account_id: str
    observed_at: datetime
    username: str | None = None
    display_name: str | None = None
    follower_count: int | None = None
    following_count: int | None = None
    post_count: int | None = None
    has_bio: bool | None = None
    bio_length: int | None = None
    has_profile_image: bool | None = None
    has_display_name: bool | None = None
    account_created_at: datetime | None = None
    is_verified: bool | None = None
    is_private: bool | None = None
    source_ref: str = ""
    payload_sha256: str = ""

    def comparable(self) -> tuple[object, ...]:
        """Everything except provenance, for exact-vs-conflicting duplicate detection."""
        return (
            self.username, self.display_name, self.follower_count, self.following_count,
            self.post_count, self.has_bio, self.bio_length, self.has_profile_image,
            self.has_display_name, self.account_created_at, self.is_verified, self.is_private,
        )


@dataclass(frozen=True)
class RelationshipRecord:
    platform: str
    source_account_id: str
    target_account_id: str
    relationship_type: RelationshipType
    observed_at: datetime
    verification_status: VerificationStatus = VerificationStatus.UNVERIFIED
    source_ref: str = ""

    def comparable(self) -> tuple[object, ...]:
        return (self.observed_at, self.verification_status)


@dataclass(frozen=True)
class ContentRecord:
    platform: str
    platform_content_id: str
    author_account_id: str
    published_at: datetime
    content_hash: str | None = None
    simhash: int | None = None  # 64-bit near-duplicate fingerprint
    text_length: int | None = None
    like_count: int | None = None
    reply_count: int | None = None
    share_count: int | None = None
    source_ref: str = ""

    def comparable(self) -> tuple[object, ...]:
        return (
            self.author_account_id, self.published_at, self.content_hash, self.simhash,
            self.like_count, self.reply_count, self.share_count,
        )


@dataclass(frozen=True)
class QuarantinedRecord:
    entity: str  # 'account' | 'relationship' | 'content'
    source_ref: str
    kind: str  # 'invalid' | 'duplicate'
    reasons: tuple[str, ...]
    raw: dict[str, object] = field(default_factory=dict)
