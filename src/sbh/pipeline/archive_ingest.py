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


@dataclass
class ExtractedArchive:
    """Metadata and paths resulting from a safely extracted dataset archive."""
    extracted_path: Path
    format: DatasetFormat
    file_count: int
    total_uncompressed_bytes: int
    manifest_path: Path | None = None
    records_path: Path | None = None
    platform_hint: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)
