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


class SafeArchiveExtractor:
    """Hardened archive unpacker defending against zip-bombs and path traversals."""

    DEFAULT_MAX_BYTES: int = 150 * 1024 * 1024  # 150 MB
    DEFAULT_MAX_RATIO: float = 100.0            # 100x uncompressed:compressed
    DEFAULT_MAX_FILES: int = 500                # Max 500 files
    DEFAULT_MAX_SINGLE_FILE: int = 50 * 1024 * 1024  # 50 MB per file
    ALLOWED_EXTENSIONS: tuple[str, ...] = (
        ".json", ".ndjson", ".jsonl", ".csv", ".js", ".txt", ".tsv"
    )

    def __init__(
        self,
        max_uncompressed_bytes: int = DEFAULT_MAX_BYTES,
        max_compression_ratio: float = DEFAULT_MAX_RATIO,
        max_files: int = DEFAULT_MAX_FILES,
        max_single_file_bytes: int = DEFAULT_MAX_SINGLE_FILE,
    ) -> None:
        self.max_uncompressed_bytes = max_uncompressed_bytes
        self.max_compression_ratio = max_compression_ratio
        self.max_files = max_files
        self.max_single_file_bytes = max_single_file_bytes
