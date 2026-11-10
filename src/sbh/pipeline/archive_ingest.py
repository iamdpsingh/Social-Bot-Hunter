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

    @staticmethod
    def is_safe_path(target_dir: Path, member_path: str) -> bool:
        """Check if an archive entry path is contained strictly within target_dir."""
        if "\x00" in member_path:
            return False
        clean = member_path.strip().replace("\\", "/")
        if clean.startswith("/") or re.match(r"^[a-zA-Z]:", clean):
            return False
        parts = clean.split("/")
        if ".." in parts:
            return False
        try:
            resolved_target = target_dir.resolve()
            dest = (resolved_target / clean).resolve()
            return dest == resolved_target or resolved_target in dest.parents
        except (ValueError, RuntimeError):
            return False

    def check_compression_ratio(self, compressed_size: int, uncompressed_size: int) -> None:
        """Enforce compression ratio defense against algorithmic zip-bombs."""
        if compressed_size > 0:
            ratio = uncompressed_size / compressed_size
            if ratio > self.max_compression_ratio:
                raise ArchiveSecurityError(
                    f"Compression ratio {ratio:.1f}x exceeds limit {self.max_compression_ratio:.1f}x (zip bomb detected)"
                )
        if uncompressed_size > self.max_uncompressed_bytes:
            raise ArchiveSecurityError(
                f"Uncompressed archive size {uncompressed_size} bytes exceeds limit of {self.max_uncompressed_bytes} bytes"
            )

    def validate_member_meta(self, filename: str, file_size: int, current_count: int) -> None:
        """Validate individual member file attributes against security quotas."""
        if current_count > self.max_files:
            raise ArchiveSecurityError(
                f"Archive file count exceeds maximum quota of {self.max_files} entries"
            )
        if file_size > self.max_single_file_bytes:
            raise ArchiveSecurityError(
                f"File '{filename}' ({file_size} bytes) exceeds maximum file limit of {self.max_single_file_bytes} bytes"
            )
        ext = Path(filename).suffix.lower()
        if ext and ext not in self.ALLOWED_EXTENSIONS:
            raise ArchiveSecurityError(
                f"Forbidden file extension '{ext}' in archive member '{filename}'"
            )
