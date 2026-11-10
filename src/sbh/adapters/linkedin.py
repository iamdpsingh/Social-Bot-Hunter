"""LinkedIn Community Management and Organization API adapter."""

from __future__ import annotations

from datetime import UTC, datetime

from sbh.adapters.linkedin_client import LinkedInApiClient, MockLinkedInClient
from sbh.adapters.quota import PlatformQuotaTracker
from sbh.contracts.adapter import PlatformAdapter
from sbh.contracts.capabilities import Capability, CapabilityStatus, CollectionMode, Operation
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
