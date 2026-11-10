"""LinkedIn Community Management and Organization API client protocol."""

from __future__ import annotations

import json
from typing import Any, Protocol, cast

from sbh.adapters.errors import (
    AuthenticationError,
    EntityNotFoundError,
    RateLimitExceededError,
)


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

    def get_organization(self, org_id: str) -> dict[str, Any]:
        """Fetch organization profile from mock data."""
        clean_id = org_id.lower().replace("company:", "").replace("urn:li:organization:", "")
        self.call_history.append({"method": "get_organization", "org_id": clean_id})

        if clean_id == "auth_error_org":
            raise AuthenticationError(
                "LinkedIn OAuth token expired or missing w_organization_social scope",
                platform="linkedin",
            )

        if clean_id == "rate_limited_org":
            raise RateLimitExceededError(
                "LinkedIn API rate limit exceeded (100 req/min)",
                platform="linkedin",
                retry_after_seconds=60,
            )

        # Lookup by key or vanity
        for k, v in self._organizations.items():
            if k == clean_id or v.get("vanity_name") == clean_id or v.get("id") == clean_id:
                return cast(dict[str, Any], json.loads(json.dumps(v)))

        raise EntityNotFoundError(
            f"LinkedIn organization '{org_id}' was not found.",
            platform="linkedin",
            entity_id=org_id,
        )

    def get_member_profile(self, vanity_name: str) -> dict[str, Any]:
        """Fetch member public profile from mock data."""
        clean_vanity = vanity_name.lower().replace("in/", "").replace("in:", "")
        self.call_history.append({"method": "get_member_profile", "vanity": clean_vanity})

        if clean_vanity in self._members:
            return cast(dict[str, Any], json.loads(json.dumps(self._members[clean_vanity])))

        raise EntityNotFoundError(
            f"LinkedIn member '{vanity_name}' was not found.",
            platform="linkedin",
            entity_id=vanity_name,
        )

    def query_posts(self, author_urn: str, count: int = 20) -> dict[str, Any]:
        """Fetch posts for author."""
        clean_id = author_urn.replace("urn:li:organization:", "").replace("company:", "")
        self.call_history.append({"method": "query_posts", "author": clean_id, "count": count})

        posts = self._posts.get(clean_id, [])
        return {
            "elements": cast(list[dict[str, Any]], json.loads(json.dumps(posts[:count]))),
            "total": len(posts),
        }
