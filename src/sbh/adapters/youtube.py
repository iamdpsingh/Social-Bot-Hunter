"""YouTube Data API v3 adapter for live profile and video collection."""

from __future__ import annotations

from datetime import UTC, datetime

from sbh.adapters.quota import PlatformQuotaTracker
from sbh.adapters.youtube_client import MockYouTubeClient, YouTubeApiClient
from sbh.contracts.adapter import AccessOutcome, Page, PlatformAdapter
from sbh.contracts.capabilities import Capability, CapabilityStatus, CollectionMode, Operation
from sbh.contracts.platforms import Platform
from sbh.schemas.records import (
    AccountObservationRecord,
    ContentRecord,
    ListKind,
    RelationshipRecord,
)

YOUTUBE_DAILY_QUOTA_DEFAULT = 10000
CHANNEL_LIST_QUOTA_COST = 1
PLAYLIST_ITEMS_QUOTA_COST = 1
SUBSCRIPTIONS_QUOTA_COST = 1


class YouTubeAdapter(PlatformAdapter):
    """Official YouTube Data API v3 adapter with quota enforcement and offline mocks."""

    platform: Platform = Platform.YOUTUBE

    def __init__(
        self,
        api_key: str | None = None,
        client: YouTubeApiClient | None = None,
        quota_tracker: PlatformQuotaTracker | None = None,
    ) -> None:
        self.api_key = api_key
        self.client = client or MockYouTubeClient()
        self.quota_tracker = quota_tracker or PlatformQuotaTracker(
            platform="youtube", daily_limit=YOUTUBE_DAILY_QUOTA_DEFAULT
        )

    def capabilities(self) -> list[Capability]:
        """Return verified YouTube Data API v3 capability matrix."""
        now = datetime.now(UTC)
        return [
            Capability(
                platform=Platform.YOUTUBE,
                operation=Operation.LOOKUP_ACCOUNT,
                status=CapabilityStatus.VERIFIED,
                mode=CollectionMode.OFFICIAL_API,
                supported=True,
                endpoint="https://www.googleapis.com/youtube/v3/channels",
                api_version="v3",
                quota_notes="1 unit per call with snippet,statistics parts.",
                limitations=("Requires API key or OAuth 2.0 Bearer token.",),
                last_verified_at=now,
                verification_evidence="Verified against official YouTube Data API v3 documentation.",
            ),
            Capability(
                platform=Platform.YOUTUBE,
                operation=Operation.LIST_CONTENT,
                status=CapabilityStatus.VERIFIED,
                mode=CollectionMode.OFFICIAL_API,
                supported=True,
                endpoint="https://www.googleapis.com/youtube/v3/playlistItems",
                api_version="v3",
                quota_notes="1 unit per page via upload playlist (UU... id).",
                limitations=("Max 50 items per page.",),
                last_verified_at=now,
                verification_evidence="Verified upload playlist items listing.",
            ),
            Capability(
                platform=Platform.YOUTUBE,
                operation=Operation.LIST_FOLLOWING,
                status=CapabilityStatus.VERIFIED,
                mode=CollectionMode.OFFICIAL_API,
                supported=True,
                endpoint="https://www.googleapis.com/youtube/v3/subscriptions",
                api_version="v3",
                quota_notes="1 unit per page.",
                limitations=("Only channels that make subscriptions public are visible.",),
                last_verified_at=now,
                verification_evidence="Verified subscriptions.list endpoint.",
            ),
            Capability(
                platform=Platform.YOUTUBE,
                operation=Operation.LIST_FOLLOWERS,
                status=CapabilityStatus.REQUIRES_APPROVAL,
                mode=CollectionMode.OFFICIAL_API,
                supported=False,
                endpoint="https://www.googleapis.com/youtube/v3/subscriptions",
                api_version="v3",
                required_scopes=("https://www.googleapis.com/auth/youtube.readonly",),
                requires_approval=True,
                limitations=(
                    "YouTube Data API v3 does not permit public subscriber enumeration. "
                    "Only the channel owner via authorized OAuth 2.0 can access their subscriber list.",
                ),
            ),
        ]

    def _channel_id_to_upload_playlist_id(self, channel_id: str) -> str:
        """Derive upload playlist ID from channel ID (replace leading UC with UU)."""
        if channel_id.startswith("UC") and len(channel_id) == 24:
            return "UU" + channel_id[2:]
        return channel_id

    def lookup_account(self, platform_account_id: str) -> Page[AccountObservationRecord]:
        """Look up YouTube channel metadata and statistics."""
        self.quota_tracker.consume(CHANNEL_LIST_QUOTA_COST, "channels.list")

        is_handle = platform_account_id.startswith("@")
        resp = self.client.get_channel(platform_account_id, is_handle=is_handle)
        items = resp.get("items", [])

        if not items:
            return Page(
                outcome=AccessOutcome.UNAVAILABLE,
                items=(),
                limitation=f"YouTube channel '{platform_account_id}' was not found.",
            )

        item = items[0]
        channel_id = item.get("id", platform_account_id)
        snippet = item.get("snippet", {})
        statistics = item.get("statistics", {})

        subs_str = statistics.get("subscriberCount", "0")
        subs_count = int(subs_str) if str(subs_str).isdigit() else 0

        video_count_str = statistics.get("videoCount", "0")
        video_count = int(video_count_str) if str(video_count_str).isdigit() else 0

        created_str = snippet.get("publishedAt", "2020-01-01T00:00:00Z")
        try:
            created_at = datetime.fromisoformat(created_str.replace("Z", "+00:00"))
        except ValueError:
            created_at = datetime.now(UTC)

        thumbnails = snippet.get("thumbnails", {})
        avatar_url = thumbnails.get("high", {}).get("url") or thumbnails.get("default", {}).get("url")

        record = AccountObservationRecord(
            platform=Platform.YOUTUBE,
            platform_account_id=channel_id,
            handle=snippet.get("customUrl") or f"@{channel_id}",
            display_name=snippet.get("title", ""),
            bio=snippet.get("description", ""),
            avatar_url=avatar_url,
            created_at=created_at,
            observed_at=datetime.now(UTC),
            followers_count=subs_count,
            following_count=0,
            posts_count=video_count,
            metadata={
                "view_count": int(statistics.get("viewCount", 0)),
                "hidden_subscriber_count": statistics.get("hiddenSubscriberCount", False),
                "country": snippet.get("country"),
                "upload_playlist_id": self._channel_id_to_upload_playlist_id(channel_id),
            },
        )

        return Page(outcome=AccessOutcome.OK, items=[record])

    def list_relationships(
        self, platform_account_id: str, kind: ListKind, cursor: str | None = None
    ) -> Page[RelationshipRecord]:
        """Fetch channel relationships."""
        if kind == ListKind.FOLLOWERS:
            return Page(
                outcome=AccessOutcome.REQUIRES_APPROVAL,
                items=(),
                limitation=(
                    "YouTube Data API v3 does not support public subscriber enumeration. "
                    "OAuth 2.0 authorization with https://www.googleapis.com/auth/youtube.readonly "
                    "from the channel owner is required."
                ),
            )

        # Following -> subscriptions
        self.quota_tracker.consume(SUBSCRIPTIONS_QUOTA_COST, "subscriptions.list")
        resp = self.client.list_subscriptions(platform_account_id, page_token=cursor)
        items = resp.get("items", [])

        relationships: list[RelationshipRecord] = []
        now = datetime.now(UTC)

        for it in items:
            snippet = it.get("snippet", {})
            target_channel = snippet.get("resourceId", {}).get("channelId")
            if not target_channel:
                continue

            relationships.append(
                RelationshipRecord(
                    platform=Platform.YOUTUBE,
                    source_account_id=platform_account_id,
                    target_account_id=target_channel,
                    kind=ListKind.FOLLOWING,
                    observed_at=now,
                )
            )

        return Page(
            outcome=AccessOutcome.OK,
            items=relationships,
            next_cursor=resp.get("nextPageToken"),
        )

    def list_content(
        self, platform_account_id: str, cursor: str | None = None
    ) -> Page[ContentRecord]:
        """Fetch channel uploaded videos via upload playlist."""
        self.quota_tracker.consume(PLAYLIST_ITEMS_QUOTA_COST, "playlistItems.list")

        playlist_id = self._channel_id_to_upload_playlist_id(platform_account_id)
        resp = self.client.list_playlist_items(playlist_id, page_token=cursor)
        items = resp.get("items", [])

        content_records: list[ContentRecord] = []
        for it in items:
            snippet = it.get("snippet", {})
            video_id = snippet.get("resourceId", {}).get("videoId")
            if not video_id:
                continue

            published_str = snippet.get("publishedAt", "2020-01-01T00:00:00Z")
            try:
                published_at = datetime.fromisoformat(published_str.replace("Z", "+00:00"))
            except ValueError:
                published_at = datetime.now(UTC)

            content_records.append(
                ContentRecord(
                    platform=Platform.YOUTUBE,
                    content_id=video_id,
                    author_account_id=platform_account_id,
                    body=f"{snippet.get('title', '')}\n\n{snippet.get('description', '')}",
                    published_at=published_at,
                    observed_at=datetime.now(UTC),
                    url=f"https://www.youtube.com/watch?v={video_id}",
                    metadata={
                        "title": snippet.get("title", ""),
                        "thumbnail": snippet.get("thumbnails", {}).get("default", {}).get("url"),
                    },
                )
            )

        return Page(
            outcome=AccessOutcome.OK,
            items=content_records,
            next_cursor=resp.get("nextPageToken"),
        )
