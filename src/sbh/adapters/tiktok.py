"""TikTok Display and Research API adapter for user lookup and video analysis."""

from __future__ import annotations

from sbh.adapters.quota import PlatformQuotaTracker
from sbh.adapters.tiktok_client import MockTikTokClient, TikTokApiClient
from sbh.contracts.adapter import PlatformAdapter
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
