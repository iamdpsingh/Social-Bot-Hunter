"""Quota tracking and accounting for third-party platform APIs."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime

from sbh.adapters.errors import QuotaExceededError


@dataclass
class PlatformQuotaTracker:
    """Tracks daily API quota consumption and enforces daily ceiling."""

    platform: str
    daily_limit: int
    units_used: int = 0
    reset_epoch: datetime = field(
        default_factory=lambda: datetime.now(UTC).replace(
            hour=0, minute=0, second=0, microsecond=0
        )
    )
    warning_ratio: float = 0.80

    @property
    def remaining_units(self) -> int:
        return max(0, self.daily_limit - self.units_used)

    @property
    def usage_ratio(self) -> float:
        if self.daily_limit <= 0:
            return 1.0
        return self.units_used / self.daily_limit

    @property
    def is_warning(self) -> bool:
        return self.usage_ratio >= self.warning_ratio

    @property
    def is_exhausted(self) -> bool:
        return self.units_used >= self.daily_limit

    def consume(self, units: int, operation_name: str = "request") -> int:
        """Consume quota units, raising QuotaExceededError if limit is breached."""
        if self.units_used + units > self.daily_limit:
            raise QuotaExceededError(
                f"Quota exceeded for {self.platform} during {operation_name}: "
                f"attempted {units} units, but only {self.remaining_units} remaining of {self.daily_limit}",
                platform=self.platform,
                units_used=self.units_used,
                daily_limit=self.daily_limit,
                resets_at=self.reset_epoch.isoformat(),
            )
        self.units_used += units
        return self.remaining_units

    def reset_if_new_day(self, now: datetime | None = None) -> bool:
        """Reset quota if current time is past the daily reset boundary."""
        now = now or datetime.now(UTC)
        if now.date() > self.reset_epoch.date():
            self.units_used = 0
            self.reset_epoch = now.replace(hour=0, minute=0, second=0, microsecond=0)
            return True
        return False
