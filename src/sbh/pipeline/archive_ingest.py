"""Archive Ingestion, Security Defense & Dataset Format Detection Engine."""

from __future__ import annotations

from enum import Enum


class ArchiveSecurityError(ValueError):
    """Raised when an archive violates safety boundaries (zip-bomb, traversal, etc)."""

class ArchiveFormatError(ValueError):
    """Raised when an archive cannot be opened or parsed."""

class DatasetFormat(str, Enum):
    """Supported dataset archive formats."""
    TWITTER_ARCHIVE = "twitter_archive"
    NDJSON = "ndjson"
    CSV = "csv"
    GENERIC_JSON = "generic_json"
    UNKNOWN = "unknown"
