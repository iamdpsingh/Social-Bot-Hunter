"""Exception hierarchy. Each error type maps to a distinct operational failure category."""

from __future__ import annotations


class SbhError(Exception):
    """Base class for all application errors."""


class ConfigError(SbhError):
    """The detection/import configuration is missing or invalid."""


class SchemaIncompatibleError(SbhError):
    """The input as a whole cannot be interpreted (bad manifest, missing columns, wrong version)."""


class ImportLimitError(SbhError):
    """The input exceeds a configured size or row limit."""


class InvalidTransitionError(SbhError):
    """A scan state change was rejected because the current state does not allow it."""


class ScanInProgressError(SbhError):
    """A scan for the same input is already running; refusing to start a second one."""


class ScanFailedError(SbhError):
    """A scan stopped because of an error. The scan row records the reason."""

    def __init__(self, scan_id: str, reason: str) -> None:
        super().__init__(f"scan {scan_id} failed: {reason}")
        self.scan_id = scan_id
        self.reason = reason


class GraphLimitExceeded(SbhError):
    """A configured graph node/edge/pair/runtime limit was hit. Results are never silently truncated."""


class TransientError(SbhError):
    """A failure that may succeed on retry (timeouts, 5xx, rate limiting)."""

    def __init__(self, message: str, retry_after: float | None = None) -> None:
        super().__init__(message)
        self.retry_after = retry_after


class PermanentError(SbhError):
    """A failure that retrying cannot fix (permission denied, unsupported operation)."""
