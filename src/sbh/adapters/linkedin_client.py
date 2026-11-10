"""LinkedIn Community Management and Organization API client protocol."""

from __future__ import annotations

from typing import Any, Protocol


class LinkedInApiClient(Protocol):
    """Protocol defining required LinkedIn API interactions."""

    def get_organization(self, org_id: str) -> dict[str, Any]:
        """Fetch organization profile and metrics from LinkedIn Community API."""
        ...

    def get_member_profile(self, vanity_name: str) -> dict[str, Any]:
        """Fetch member public profile from OpenID / UserInfo."""
        ...

    def query_posts(self, author_urn: str, count: int = 20) -> dict[str, Any]:
        """Fetch organization share updates and posts."""
        ...


class MockLinkedInClient:
    """Offline mock LinkedIn Community & Member API fixture replay player."""

    def __init__(self) -> None:
        self.call_history: list[dict[str, Any]] = []
        self._organizations: dict[str, dict[str, Any]] = {
            "tech_corp": {
                "id": "10001",
                "urn": "urn:li:organization:10001",
                "vanity_name": "tech-corp",
                "name": "Tech Corp International",
                "tagline": "Pioneering AI systems and transparent cyber intelligence.",
                "website": "https://techcorp.example.com",
                "logo_url": "https://media.licdn.com/dms/image/v2/logo1.jpg",
                "follower_count": 250000,
                "staff_count": 1400,
                "post_count": 85,
            },
            "bot_staffing_agency": {
                "id": "10099",
                "urn": "urn:li:organization:10099",
                "vanity_name": "instant-placement",
                "name": "Instant Staffing Solutions",
                "tagline": "Guaranteed remote placements DM for details",
                "website": "http://scam-agency.info",
                "logo_url": "",
                "follower_count": 15,
                "staff_count": 2,
                "post_count": 6,
            },
        }
        self._members: dict[str, dict[str, Any]] = {
            "satyanadella": {
                "id": "5001",
                "urn": "urn:li:person:5001",
                "vanity_name": "satyanadella",
                "name": "Satya Nadella",
                "headline": "Chairman and CEO at Microsoft",
                "avatar_url": "https://media.licdn.com/dms/image/v2/satya.jpg",
                "follower_count": 10500000,
                "is_influencer": True,
            },
        }
        self._posts: dict[str, list[dict[str, Any]]] = {
            "10001": [
                {
                    "id": "urn:li:share:7200000001",
                    "text": "Announcing our new open-source social network auditing framework #opensource #ai",
                    "created_at": 1731100000,
                    "like_count": 1400,
                    "comment_count": 65,
                    "share_count": 120,
                },
                {
                    "id": "urn:li:share:7200000002",
                    "text": "Empowering organizations to detect coordinated bot behaviour across social platforms.",
                    "created_at": 1731000000,
                    "like_count": 890,
                    "comment_count": 32,
                    "share_count": 45,
                },
            ],
        }
