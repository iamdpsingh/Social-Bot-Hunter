"""Instagram Graph API adapter for Business Discovery and media inspection."""

from __future__ import annotations

from sbh.adapters.instagram_client import InstagramApiClient, MockInstagramClient
from sbh.adapters.quota import PlatformQuotaTracker
from sbh.contracts.adapter import PlatformAdapter
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
