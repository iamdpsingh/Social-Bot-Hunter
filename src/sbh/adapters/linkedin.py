"""LinkedIn Community Management and Organization API adapter."""

from __future__ import annotations

from sbh.adapters.linkedin_client import LinkedInApiClient, MockLinkedInClient
from sbh.adapters.quota import PlatformQuotaTracker
from sbh.contracts.adapter import PlatformAdapter
from sbh.contracts.platforms import Platform

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
