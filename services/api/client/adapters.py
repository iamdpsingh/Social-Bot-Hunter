"""SDK client wrapper for Adapters API endpoints."""

from __future__ import annotations

from typing import Any

from services.api.client.session import ApiSession


class AdaptersClient:
    """Client for profile URL validation, preflight probing, and quota telemetry."""

    def __init__(self, session: ApiSession) -> None:
        self.session = session

    def validate_url(self, url: str, platform_hint: str | None = None) -> dict[str, Any]:
        payload: dict[str, Any] = {"url": url}
        if platform_hint:
            payload["platform_hint"] = platform_hint
        resp = self.session.post("/api/v1/adapters/validate-url", json=payload)
        resp.raise_for_status()
        return resp.json()

    def probe(self, url: str, platform_hint: str | None = None) -> dict[str, Any]:
        payload: dict[str, Any] = {"url": url}
        if platform_hint:
            payload["platform_hint"] = platform_hint
        resp = self.session.post("/api/v1/adapters/probe", json=payload)
        resp.raise_for_status()
        return resp.json()

    def get_quotas(self) -> list[dict[str, Any]]:
        resp = self.session.get("/api/v1/adapters/quotas")
        resp.raise_for_status()
        return resp.json()

    def get_telemetry(self) -> dict[str, Any]:
        resp = self.session.get("/api/v1/adapters/telemetry")
        resp.raise_for_status()
        return resp.json()
