"""Authentication operations sub-client."""

from __future__ import annotations

from services.api.client.session import ApiSession


class AuthClient:
    """Client for auth endpoints."""

    def __init__(self, session: ApiSession) -> None:
        self.session = session

    def login_path(self) -> str:
        return "/api/v1/auth/login"

    def refresh_path(self) -> str:
        return "/api/v1/auth/refresh"

    def me_path(self) -> str:
        return "/api/v1/auth/me"
