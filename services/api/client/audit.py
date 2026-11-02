"""Compliance audit sub-client."""

from __future__ import annotations

from services.api.client.session import ApiSession


class AuditClient:
    """Client for audit endpoints."""

    def __init__(self, session: ApiSession) -> None:
        self.session = session

    def audit_path(self) -> str:
        return "/api/v1/audit"
