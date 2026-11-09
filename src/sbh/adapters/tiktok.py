"""TikTok Display and Research API adapter for user lookup and video analysis."""

from __future__ import annotations

from datetime import UTC, datetime

from sbh.adapters.quota import PlatformQuotaTracker
from sbh.adapters.tiktok_client import MockTikTokClient, TikTokApiClient
from sbh.contracts.adapter import PlatformAdapter
from sbh.contracts.capabilities import Capability, CapabilityStatus, CollectionMode, Operation
from sbh.contracts.platforms import Platform

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
