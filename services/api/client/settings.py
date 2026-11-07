"""Settings and retention subclient for SocialBotHunterClient SDK."""

from __future__ import annotations

from services.api.client.session import ApiSession
from services.api.schemas import PlatformQuotaStatus, RetentionPurgeResponse, RetentionStatsResponse


class SettingsClient:
    """Client for platform capabilities, quotas, and retention cleanup."""

    def __init__(self, session: ApiSession) -> None:
        self.session = session

    def get_retention_stats(self, retention_days: int = 90) -> RetentionStatsResponse:
        """Fetch current data retention metrics."""
        res = self.session.get("/api/v1/settings/retention", params={"retention_days": retention_days})
        return RetentionStatsResponse.model_validate(res.json())

    def purge_retention(self, retention_days: int = 90, dry_run: bool = False) -> RetentionPurgeResponse:
        """Trigger dry-run or atomic purge of expired scans."""
        res = self.session.post(
            "/api/v1/settings/retention/purge",
            json={"retention_days": retention_days, "dry_run": dry_run},
        )
        return RetentionPurgeResponse.model_validate(res.json())

    def get_quotas(self) -> list[PlatformQuotaStatus]:
        """Fetch platform quota limits and remaining usage."""
        res = self.session.get("/api/v1/settings/quotas")
        return [PlatformQuotaStatus.model_validate(q) for q in res.json()]
