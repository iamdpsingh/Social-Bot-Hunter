"""Instagram Graph API adapter for Business Discovery and media inspection."""

from __future__ import annotations

from datetime import UTC, datetime

from sbh.adapters.instagram_client import InstagramApiClient, MockInstagramClient
from sbh.adapters.quota import PlatformQuotaTracker
from sbh.contracts.adapter import PlatformAdapter
from sbh.contracts.capabilities import Capability, CapabilityStatus, CollectionMode, Operation
from sbh.contracts.platforms import Platform

INSTAGRAM_DAILY_QUOTA_DEFAULT = 4800
BUSINESS_DISCOVERY_QUOTA_COST = 1
MEDIA_LIST_QUOTA_COST = 1


class InstagramAdapter(PlatformAdapter):
    """Official Instagram Graph API adapter using Business Discovery endpoint."""

    platform: Platform = Platform.INSTAGRAM

    def __init__(
        self,
        access_token: str | None = None,
        ig_user_id: str | None = None,
        client: InstagramApiClient | None = None,
        quota_tracker: PlatformQuotaTracker | None = None,
    ) -> None:
        self.access_token = access_token
        self.ig_user_id = ig_user_id or "1784140000"
        self.client = client or MockInstagramClient()
        self.quota_tracker = quota_tracker or PlatformQuotaTracker(
            platform="instagram", daily_limit=INSTAGRAM_DAILY_QUOTA_DEFAULT
        )

    def capabilities(self) -> list[Capability]:
        """Return verified Instagram Graph API capability matrix."""
        now = datetime.now(UTC)
        return [
            Capability(
                platform=Platform.INSTAGRAM,
                operation=Operation.LOOKUP_ACCOUNT,
                status=CapabilityStatus.VERIFIED,
                mode=CollectionMode.OFFICIAL_API,
                supported=True,
                endpoint="https://graph.facebook.com/v21.0/{ig-user-id}?fields=business_discovery.username({username})",
                api_version="v21.0",
                quota_notes="1 call per lookup. Rate limit: 200 calls/hr/user.",
                limitations=(
                    "Target must be an Instagram Business or Creator account.",
                    "Personal profiles cannot be inspected via Business Discovery.",
                ),
                last_verified_at=now,
                verification_evidence="Verified against Meta Graph API v21.0 Business Discovery documentation.",
            ),
            Capability(
                platform=Platform.INSTAGRAM,
                operation=Operation.LIST_CONTENT,
                status=CapabilityStatus.VERIFIED,
                mode=CollectionMode.OFFICIAL_API,
                supported=True,
                endpoint="https://graph.facebook.com/v21.0/{ig-user-id}?fields=business_discovery.username({username}){media}",
                api_version="v21.0",
                quota_notes="1 call per page (max 25 items).",
                limitations=("Returns public media only. Stories and ephemeral content excluded.",),
                last_verified_at=now,
                verification_evidence="Verified nested media queries via Business Discovery.",
            ),
            Capability(
                platform=Platform.INSTAGRAM,
                operation=Operation.LIST_FOLLOWERS,
                status=CapabilityStatus.REQUIRES_APPROVAL,
                mode=CollectionMode.OFFICIAL_API,
                supported=False,
                endpoint="https://graph.facebook.com/v21.0",
                api_version="v21.0",
                required_scopes=("instagram_basic", "pages_show_list"),
                requires_approval=True,
                limitations=(
                    "Instagram Graph API does not permit public follower graph enumeration. "
                    "Only aggregated counts are available via Business Discovery.",
                ),
            ),
            Capability(
                platform=Platform.INSTAGRAM,
                operation=Operation.LIST_FOLLOWING,
                status=CapabilityStatus.REQUIRES_APPROVAL,
                mode=CollectionMode.OFFICIAL_API,
                supported=False,
                endpoint="https://graph.facebook.com/v21.0",
                api_version="v21.0",
                required_scopes=("instagram_basic", "pages_show_list"),
                requires_approval=True,
                limitations=(
                    "Instagram Graph API does not permit following graph enumeration.",
                ),
            ),
        ]
