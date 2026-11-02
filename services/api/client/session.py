"""Authenticated client session."""

from __future__ import annotations

from typing import Any
from services.api.client.config import ClientConfig
from services.api.client.exceptions import AuthenticationError, AuthorizationError, NotFoundError, RateLimitError, SBHClientError


class ApiSession:
    """Session managing headers and authentication tokens."""

    def __init__(self, config: ClientConfig) -> None:
        self.config = config
        self.token: str | None = None

    def set_token(self, token: str) -> None:
        self.token = token

    def headers(self) -> dict[str, str]:
        h = {"Content-Type": "application/json", "Accept": "application/json"}
        if self.token:
            h["Authorization"] = f"Bearer {self.token}"
        return h
