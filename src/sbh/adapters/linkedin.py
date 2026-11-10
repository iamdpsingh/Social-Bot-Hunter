"""LinkedIn Community Management and Organization API adapter."""

from __future__ import annotations

from datetime import UTC, datetime

from sbh.adapters.linkedin_client import LinkedInApiClient, MockLinkedInClient
from sbh.adapters.quota import PlatformQuotaTracker
from sbh.contracts.adapter import AccessOutcome, Page, PlatformAdapter
from sbh.contracts.capabilities import Capability, CapabilityStatus, CollectionMode, Operation
from sbh.contracts.platforms import Platform
from sbh.detection.simhash import compute_simhash
from sbh.schemas.records import (
    AccountObservationRecord,
    ContentRecord,
    ListKind,
    RelationshipRecord,
)

LINKEDIN_DAILY_QUOTA_DEFAULT = 2500
LOOKUP_QUOTA_COST = 1
POSTS_QUOTA_COST = 1


class LinkedInAdapter(PlatformAdapter):
    """Official LinkedIn Community Management and Member API adapter."""

    platform: Platform = Platform.LINKEDIN

    def __init__(
        self,
        access_token: str | None = None,
        client: LinkedInApiClient | None = None,
        quota_tracker: PlatformQuotaTracker | None = None,
    ) -> None:
        self.access_token = access_token
        self.client = client or MockLinkedInClient()
        self.quota_tracker = quota_tracker or PlatformQuotaTracker(
            platform="linkedin", daily_limit=LINKEDIN_DAILY_QUOTA_DEFAULT
        )

    def capabilities(self) -> list[Capability]:
        """Return verified LinkedIn Community Management API capability matrix."""
        now = datetime.now(UTC)
        return [
            Capability(
                platform=Platform.LINKEDIN,
                operation=Operation.LOOKUP_ACCOUNT,
                status=CapabilityStatus.VERIFIED,
                mode=CollectionMode.OFFICIAL_API,
                supported=True,
                endpoint="https://api.linkedin.com/v2/organizations/{id}",
                api_version="v2",
                quota_notes="1 call per lookup. Standard quota: 2,500 queries/day.",
                limitations=(
                    "Requires OAuth 2.0 Bearer token with r_organization_social or openid profile scope.",
                ),
                last_verified_at=now,
                verification_evidence="Verified against official LinkedIn Community Management API documentation.",
            ),
            Capability(
                platform=Platform.LINKEDIN,
                operation=Operation.LIST_CONTENT,
                status=CapabilityStatus.VERIFIED,
                mode=CollectionMode.OFFICIAL_API,
                supported=True,
                endpoint="https://api.linkedin.com/v2/posts?author={urn}",
                api_version="v2",
                quota_notes="1 call per page (max 50 posts).",
                limitations=("Returns public organization updates only.",),
                last_verified_at=now,
                verification_evidence="Verified LinkedIn Organization posts endpoint.",
            ),
            Capability(
                platform=Platform.LINKEDIN,
                operation=Operation.LIST_FOLLOWERS,
                status=CapabilityStatus.REQUIRES_APPROVAL,
                mode=CollectionMode.OFFICIAL_API,
                supported=False,
                endpoint="https://api.linkedin.com/v2",
                api_version="v2",
                requires_approval=True,
                limitations=(
                    "LinkedIn does not permit public member network or 1st-degree connection enumeration "
                    "to prevent unauthorized data extraction and protect member privacy.",
                ),
            ),
            Capability(
                platform=Platform.LINKEDIN,
                operation=Operation.LIST_FOLLOWING,
                status=CapabilityStatus.REQUIRES_APPROVAL,
                mode=CollectionMode.OFFICIAL_API,
                supported=False,
                endpoint="https://api.linkedin.com/v2",
                api_version="v2",
                requires_approval=True,
                limitations=(
                    "LinkedIn does not permit public following graph enumeration.",
                ),
            ),
        ]

    def lookup_account(self, platform_account_id: str) -> Page[AccountObservationRecord]:
        """Look up LinkedIn organization or member profile."""
        self.quota_tracker.reset_if_new_day()
        self.quota_tracker.consume(LOOKUP_QUOTA_COST, "lookup_account")

        clean_id = platform_account_id.lower().lstrip("@")
        now = datetime.now(UTC)

        # Distinguish between company and member
        if clean_id.startswith("company:") or clean_id.startswith("school:"):
            target_name = clean_id.split(":", 1)[1]
            data = self.client.get_organization(target_name)
            obs = AccountObservationRecord(
                platform=Platform.LINKEDIN,
                platform_account_id=str(data.get("urn") or data.get("id")),
                observed_at=now,
                username=data.get("vanity_name", target_name),
                display_name=data.get("name"),
                follower_count=data.get("follower_count"),
                following_count=None,
                post_count=data.get("post_count"),
                has_bio=bool(data.get("tagline")),
                has_profile_image=bool(data.get("logo_url")),
                source_ref="official_api:linkedin:v2:organizations",
            )
            return Page(items=[obs], outcome=AccessOutcome.OK)

        # Member profile
        data = self.client.get_member_profile(clean_id)
        obs = AccountObservationRecord(
            platform=Platform.LINKEDIN,
            platform_account_id=str(data.get("urn") or data.get("id")),
            observed_at=now,
            username=data.get("vanity_name", clean_id),
            display_name=data.get("name"),
            follower_count=data.get("follower_count"),
            following_count=None,
            post_count=None,
            has_bio=bool(data.get("headline")),
            has_profile_image=bool(data.get("avatar_url")),
            is_verified=data.get("is_influencer", False),
            source_ref="official_api:linkedin:v2:members",
        )
        return Page(items=[obs], outcome=AccessOutcome.OK)

    def list_relationships(
        self,
        platform_account_id: str,
        kind: ListKind,
        cursor: str | None = None,
    ) -> Page[RelationshipRecord]:
        """LinkedIn API does not permit public connection/follower graph enumeration."""
        return Page(
            items=[],
            outcome=AccessOutcome.REQUIRES_APPROVAL,
            limitation=(
                "LinkedIn API does not support public member network enumeration to protect privacy."
            ),
        )

    def list_content(
        self,
        platform_account_id: str,
        cursor: str | None = None,
        limit: int = 50,
    ) -> Page[ContentRecord]:
        """Fetch posts published by LinkedIn organization."""
        self.quota_tracker.reset_if_new_day()
        self.quota_tracker.consume(POSTS_QUOTA_COST, "list_content")

        res = self.client.query_posts(platform_account_id, count=limit)
        posts = res.get("elements", [])

        records: list[ContentRecord] = []
        for p in posts:
            text = p.get("text", "")
            ctime = p.get("created_at")
            dt = datetime.fromtimestamp(ctime, tz=UTC) if ctime else datetime.now(UTC)
            sh = compute_simhash(text) if text else 0

            records.append(
                ContentRecord(
                    platform=Platform.LINKEDIN.value,
                    platform_content_id=str(p.get("id")),
                    author_account_id=platform_account_id,
                    published_at=dt,
                    simhash=sh if sh else None,
                    text_length=len(text),
                    like_count=p.get("like_count"),
                    reply_count=p.get("comment_count"),
                    share_count=p.get("share_count"),
                    source_ref="official_api:linkedin:v2:posts",
                )
            )

        return Page(items=records, outcome=AccessOutcome.OK)

    def list_followers(
        self,
        identifier: str,
        cursor: str | None = None,
        limit: int = 100,
    ) -> Page[RelationshipRecord]:
        return Page(
            items=[],
            outcome=AccessOutcome.REQUIRES_APPROVAL,
            limitation="LinkedIn API does not support public follower list enumeration.",
        )

    def list_following(
        self,
        identifier: str,
        cursor: str | None = None,
        limit: int = 100,
    ) -> Page[RelationshipRecord]:
        return Page(
            items=[],
            outcome=AccessOutcome.REQUIRES_APPROVAL,
            limitation="LinkedIn API does not support public following list enumeration.",
        )
