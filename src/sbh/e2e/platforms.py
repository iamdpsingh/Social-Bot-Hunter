"""Multi-platform synthetic account generator for end-to-end acceptance tests."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any


@dataclass
class PlatformSampleAccount:
    """Standardized multi-platform account fixture representation."""

    platform: str
    account_id: str
    username: str
    display_name: str
    followers_count: int
    following_count: int
    post_count: int
    created_at: str
    bio: str
    is_bot_ground_truth: bool
    recent_texts: list[str] = field(default_factory=list)
    coordination_group: str | None = None


class MultiPlatformMockGenerator:
    """Generates synthetic multi-platform account clusters for acceptance testing."""

    SUPPORTED_PLATFORMS = ("twitter", "bluesky", "mastodon", "reddit", "youtube")

    @classmethod
    def generate_campaign_accounts(
        cls,
        platform: str,
        campaign_size: int = 5,
        target_topic: str = "crypto_airdrop",
    ) -> list[PlatformSampleAccount]:
        """Generate a cluster of coordinated bot accounts for a platform."""
        accounts: list[PlatformSampleAccount] = []
        now = datetime.now(timezone.utc).isoformat()
        campaign_text = f"Claim free token immediately at claim-{target_topic}.org! 🚀 Guaranteed reward"

        for i in range(campaign_size):
            acc = PlatformSampleAccount(
                platform=platform,
                account_id=f"{platform}_bot_{i+1:03d}",
                username=f"{platform}_bot_{i+1:03d}",
                display_name=f"Crypto Bot {i+1}",
                followers_count=12,
                following_count=450,
                post_count=85,
                created_at=now,
                bio=f"Official updates and {target_topic} rewards 🤖",
                is_bot_ground_truth=True,
                recent_texts=[
                    campaign_text,
                    f"Check out the latest {target_topic} announcement!",
                    campaign_text,
                ],
                coordination_group=f"{platform}_{target_topic}",
            )
            accounts.append(acc)

        return accounts

    @classmethod
    def generate_human_account(cls, platform: str, handle: str) -> PlatformSampleAccount:
        """Generate a realistic human account."""
        return PlatformSampleAccount(
            platform=platform,
            account_id=f"{platform}_human_{handle}",
            username=handle,
            display_name=f"{handle.capitalize()} User",
            followers_count=520,
            following_count=380,
            post_count=1450,
            created_at="2020-01-15T12:00:00Z",
            bio="Software engineer, open source enthusiast, coffee lover.",
            is_bot_ground_truth=False,
            recent_texts=[
                "Working on a new Python library today.",
                "Nice weather outside for a weekend hike.",
                "Reviewing pull requests and writing documentation.",
            ],
            coordination_group=None,
        )
