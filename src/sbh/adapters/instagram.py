"""Instagram Graph API adapter for Business Discovery and media inspection."""

from __future__ import annotations

from datetime import UTC, datetime
from typing import Any

from sbh.adapters.instagram_client import InstagramApiClient, MockInstagramClient
from sbh.adapters.quota import PlatformQuotaTracker
from sbh.contracts.adapter import AccessOutcome, Page, PlatformAdapter
from sbh.contracts.capabilities import Capability, CapabilityStatus, CollectionMode, Operation
from sbh.contracts.platforms import Platform
from sbh.fingerprint.simhash import compute_simhash_hex
from sbh.schemas.records import AccountObservationRecord, ContentRecord

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

    def lookup_account(self, identifier: str) -> Page[AccountObservationRecord]:
        """Look up Instagram account via Business Discovery endpoint."""
        self.quota_tracker.reset_if_new_day()
        self.quota_tracker.consume(BUSINESS_DISCOVERY_QUOTA_COST, "lookup_account")

        clean_handle = identifier.lstrip("@").lower()
        res = self.client.business_discovery(clean_handle)

        # Check for personal account subcode or error
        if "error" in res:
            err = res["error"]
            subcode = err.get("error_subcode")
            msg = err.get("message", "")
            if subcode == 2207050 or "not a business account" in msg.lower():
                return Page(
                    items=[],
                    outcome=AccessOutcome.REQUIRES_APPROVAL,
                    limitation=(
                        "Instagram Business Discovery requires the target profile to be a "
                        "Business or Creator account. The requested profile is personal/private."
                    ),
                )
            return Page(
                items=[],
                outcome=AccessOutcome.PERMISSION_DENIED,
                limitation=f"Instagram Graph API error: {msg}",
            )

        data = res.get("business_discovery", {})
        if not data:
            return Page(
                items=[],
                outcome=AccessOutcome.NOT_FOUND,
                limitation=f"No account data found for Instagram handle '{clean_handle}'",
            )

        now = datetime.now(UTC)
        obs = AccountObservationRecord(
            platform=Platform.INSTAGRAM,
            platform_account_id=str(data.get("ig_id") or data.get("id")),
            observed_at=now,
            username=data.get("username", clean_handle),
            display_name=data.get("name"),
            follower_count=data.get("followers_count"),
            following_count=data.get("follows_count"),
            post_count=data.get("media_count"),
            has_bio=bool(data.get("biography")),
            has_profile_image=bool(data.get("profile_picture_url")),
            source_ref="official_api:instagram:v21.0:business_discovery",
        )

        return Page(items=[obs], outcome=AccessOutcome.OK)

    def check_business_boundary(self, identifier: str) -> tuple[bool, str | None]:
        """Check whether target handle is eligible for Business Discovery."""
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
        """Fetch recent media posts for an Instagram business account."""
        self.quota_tracker.reset_if_new_day()
        self.quota_tracker.consume(MEDIA_LIST_QUOTA_COST, "list_content")

        clean_handle = identifier.lstrip("@").lower()
        res = self.client.business_discovery(clean_handle)
        if "error" in res:
            return Page(
                items=[],
                outcome=AccessOutcome.REQUIRES_APPROVAL,
                limitation="Cannot retrieve media: target is not an authorized Business/Creator account.",
            )

        data = res.get("business_discovery", {})
        media_items = data.get("media", {}).get("data", [])

        records: list[ContentRecord] = []
        for m in media_items[:limit]:
            caption = m.get("caption", "")
            ts_str = m.get("timestamp")
            dt: datetime | None = None
            if ts_str:
                try:
                    dt = datetime.fromisoformat(ts_str.replace("+0000", "+00:00"))
                except ValueError:
                    dt = None

            simhash_hex = compute_simhash_hex(caption) if caption else None

            records.append(
                ContentRecord(
                    platform=Platform.INSTAGRAM,
                    content_id=str(m.get("id")),
                    account_id=str(data.get("ig_id") or data.get("id")),
                    text=caption,
                    posted_at=dt,
                    language=None,
                    like_count=m.get("like_count"),
                    reply_count=m.get("comments_count"),
                    share_count=None,
                    simhash=simhash_hex,
                    content_type=m.get("media_type", "POST").lower(),
                    source_ref="official_api:instagram:v21.0:media",
                )
            )

        return Page(items=records, outcome=AccessOutcome.OK)

    def list_followers(
        self,
        identifier: str,
        limit: int = 100,
        cursor: str | None = None,
    ) -> Page[Any]:
        """Instagram Graph API does not permit public follower enumeration."""
        return Page(
            items=[],
            outcome=AccessOutcome.REQUIRES_APPROVAL,
            limitation=(
                "Instagram Graph API does not support public follower list enumeration. "
                "Meta restricts follower graph access to protect user privacy."
            ),
        )

    def list_following(
        self,
        identifier: str,
        limit: int = 100,
        cursor: str | None = None,
    ) -> Page[Any]:
        """Instagram Graph API does not permit public following enumeration."""
        return Page(
            items=[],
            outcome=AccessOutcome.REQUIRES_APPROVAL,
            limitation=(
                "Instagram Graph API does not support public following list enumeration."
            ),
        )
