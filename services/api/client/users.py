"""User management operations sub-client."""

from __future__ import annotations

from services.api.client.session import ApiSession


class UsersClient:
    """Client for user management endpoints."""

    def __init__(self, session: ApiSession) -> None:
        self.session = session

    def users_path(self) -> str:
        return "/api/v1/users"
