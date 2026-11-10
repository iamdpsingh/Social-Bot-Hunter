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
