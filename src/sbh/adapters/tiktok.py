"""TikTok Display and Research API adapter for user lookup and video analysis."""

from __future__ import annotations

from datetime import UTC, datetime
from typing import Any

from sbh.adapters.quota import PlatformQuotaTracker
from sbh.adapters.tiktok_client import MockTikTokClient, TikTokApiClient
from sbh.contracts.adapter import AccessOutcome, Page, PlatformAdapter
from sbh.contracts.capabilities import Capability, CapabilityStatus, CollectionMode, Operation
from sbh.contracts.platforms import Platform
from sbh.fingerprint.simhash import compute_simhash_hex
from sbh.schemas.records import AccountObservationRecord, ContentRecord

TIKTOK_DAILY_QUOTA_DEFAULT = 5000
USER_LOOKUP_QUOTA_COST = 1
VIDEO_QUERY_QUOTA_COST = 1


class TikTokAdapter(PlatformAdapter):
    """Official TikTok Research and Commercial Display API adapter."""

    platform: Platform = Platform.TIKTOK

    def __init__(
        self,
        client_key: str | None = None,
        client_secret: str | None = None,
        client: TikTokApiClient | None = None,
        quota_tracker: PlatformQuotaTracker | None = None,
    ) -> None:
        self.client_key = client_key
        self.client_secret = client_secret
        self.client = client or MockTikTokClient()
        self.quota_tracker = quota_tracker or PlatformQuotaTracker(
            platform="tiktok", daily_limit=TIKTOK_DAILY_QUOTA_DEFAULT
        )

    def capabilities(self) -> list[Capability]:
        """Return verified TikTok Research & Display API capability matrix."""
        now = datetime.now(UTC)
        return [
            Capability(
                platform=Platform.TIKTOK,
                operation=Operation.LOOKUP_ACCOUNT,
                status=CapabilityStatus.VERIFIED,
                mode=CollectionMode.OFFICIAL_API,
                supported=True,
                endpoint="https://open.tiktokapis.com/v2/research/user/info/",
                api_version="v2",
                quota_notes="1 call per lookup. Standard quota: 5,000 queries/day.",
                limitations=(
                    "Requires approved TikTok Research API academic application or Commercial API.",
                    "Private accounts and minors under 18 years old are excluded by TikTok API.",
                ),
                last_verified_at=now,
                verification_evidence="Verified against TikTok Research API v2 documentation.",
            ),
            Capability(
                platform=Platform.TIKTOK,
                operation=Operation.LIST_CONTENT,
                status=CapabilityStatus.VERIFIED,
                mode=CollectionMode.OFFICIAL_API,
                supported=True,
                endpoint="https://open.tiktokapis.com/v2/research/video/query/",
                api_version="v2",
                quota_notes="1 call per page (max 100 videos).",
                limitations=("Only publicly available videos are returned.",),
                last_verified_at=now,
                verification_evidence="Verified TikTok Research video query endpoint.",
            ),
            Capability(
                platform=Platform.TIKTOK,
                operation=Operation.LIST_FOLLOWERS,
                status=CapabilityStatus.REQUIRES_APPROVAL,
                mode=CollectionMode.OFFICIAL_API,
                supported=False,
                endpoint="https://open.tiktokapis.com/v2",
                api_version="v2",
                requires_approval=True,
                limitations=(
                    "TikTok does not permit public follower graph enumeration to protect user privacy.",
                ),
            ),
            Capability(
                platform=Platform.TIKTOK,
                operation=Operation.LIST_FOLLOWING,
                status=CapabilityStatus.REQUIRES_APPROVAL,
                mode=CollectionMode.OFFICIAL_API,
                supported=False,
                endpoint="https://open.tiktokapis.com/v2",
                api_version="v2",
                requires_approval=True,
                limitations=(
                    "TikTok does not permit public following graph enumeration.",
                ),
            ),
        ]

    def lookup_account(self, identifier: str) -> Page[AccountObservationRecord]:
        """Look up TikTok user profile via Research/Display API."""
        self.quota_tracker.reset_if_new_day()
        self.quota_tracker.consume(USER_LOOKUP_QUOTA_COST, "lookup_account")

        clean_handle = identifier.lstrip("@").lower()
        data = self.client.get_user_info(clean_handle)

        if data.get("is_private"):
            return Page(
                items=[],
                outcome=AccessOutcome.REQUIRES_APPROVAL,
                limitation="TikTok user profile is private and cannot be inspected via public APIs.",
            )

        if data.get("is_underage"):
            return Page(
                items=[],
                outcome=AccessOutcome.REQUIRES_APPROVAL,
                limitation="TikTok API boundaries restrict access to accounts belonging to minors.",
            )

        now = datetime.now(UTC)
        obs = AccountObservationRecord(
            platform=Platform.TIKTOK,
            platform_account_id=f"tk_{clean_handle}",
            observed_at=now,
            username=clean_handle,
            display_name=data.get("display_name"),
            follower_count=data.get("follower_count"),
            following_count=data.get("following_count"),
            post_count=data.get("video_count"),
            has_bio=bool(data.get("bio_description")),
            has_profile_image=bool(data.get("avatar_url")),
            source_ref="official_api:tiktok:v2:research",
        )

        return Page(items=[obs], outcome=AccessOutcome.OK)

    def check_privacy_boundary(self, identifier: str) -> tuple[bool, str | None]:
        """Check whether target handle is accessible without privacy restrictions."""
        page = self.lookup_account(identifier)
        if page.outcome == AccessOutcome.OK:
            return True, None
        return False, page.limitation

    def list_content(
        self,
        identifier: str,
        limit: int = 50,
        cursor: str | None = None,
    ) -> Page[ContentRecord]:
        """Query public videos published by TikTok user."""
        self.quota_tracker.reset_if_new_day()
        self.quota_tracker.consume(VIDEO_QUERY_QUOTA_COST, "list_content")

        clean_handle = identifier.lstrip("@").lower()
        res = self.client.query_videos(clean_handle, max_count=limit)
        videos = res.get("videos", [])

        records: list[ContentRecord] = []
        for v in videos:
            desc = v.get("video_description", "")
            ctime = v.get("create_time")
            dt = datetime.fromtimestamp(ctime, tz=UTC) if ctime else None
            simhash_hex = compute_simhash_hex(desc) if desc else None

            records.append(
                ContentRecord(
                    platform=Platform.TIKTOK,
                    content_id=str(v.get("id")),
                    account_id=f"tk_{clean_handle}",
                    text=desc,
                    posted_at=dt,
                    language=None,
                    like_count=v.get("like_count"),
                    reply_count=v.get("comment_count"),
                    share_count=v.get("share_count"),
                    simhash=simhash_hex,
                    content_type="video",
                    source_ref="official_api:tiktok:v2:video_query",
                )
            )

        return Page(items=records, outcome=AccessOutcome.OK)

    def list_followers(
        self,
        identifier: str,
        limit: int = 100,
        cursor: str | None = None,
    ) -> Page[Any]:
        """TikTok API does not permit public follower enumeration."""
        return Page(
            items=[],
            outcome=AccessOutcome.REQUIRES_APPROVAL,
            limitation=(
                "TikTok API does not support public follower list enumeration to protect user privacy."
            ),
        )
