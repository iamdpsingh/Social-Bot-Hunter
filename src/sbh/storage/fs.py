"""Local filesystem storage management with path-traversal safety and SHA-256."""

from __future__ import annotations

import hashlib
import os
import tempfile
from dataclasses import asdict, dataclass
from enum import Enum
from pathlib import Path
from typing import Any


class StorageCategory(str, Enum):
    SNAPSHOTS = "snapshots"
    MODELS = "models"
    EXPORTS = "exports"
    BACKUPS = "backups"
    TEMP = "temp"


@dataclass(frozen=True)
class DirectoryStats:
    """Aggregated disk statistics for a storage category directory."""

    category: str
    path: str
    file_count: int
    total_bytes: int
    oldest_timestamp: float | None
    newest_timestamp: float | None

    @property
    def total_mb(self) -> float:
        return round(self.total_bytes / (1024 * 1024), 2)

    def to_dict(self) -> dict[str, Any]:
        d = asdict(self)
        d["total_mb"] = self.total_mb
        return d


@dataclass(frozen=True)
class AssetInfo:
    """Metadata for an individual stored asset file."""

    filename: str
    relative_path: str
    absolute_path: str
    size_bytes: int
    sha256: str
    modified_epoch: float

    @property
    def size_mb(self) -> float:
        return round(self.size_bytes / (1024 * 1024), 2)

    def to_dict(self) -> dict[str, Any]:
        d = asdict(self)
        d["size_mb"] = self.size_mb
        return d


def compute_sha256(path: Path) -> str:
    """Compute hex SHA-256 digest of a file in 64KB chunks."""
    h = hashlib.sha256()
    with open(path, "rb") as f:
        while chunk := f.read(65536):
            h.update(chunk)
    return h.hexdigest()


class LocalStorageManager:
    """Manager for local repository data categories with path-traversal safety."""

    def __init__(self, base_dir: Path | None = None) -> None:
        self.base_dir = (base_dir or Path.cwd()).resolve() / "data"

    def get_category_dir(self, category: StorageCategory) -> Path:
        """Get directory path for a storage category, creating if absent."""
        p = self.base_dir / category.value
        p.mkdir(parents=True, exist_ok=True)
        return p

    def ensure_all_dirs(self) -> dict[str, Path]:
        """Ensure all storage category directories exist."""
        res: dict[str, Path] = {}
        for cat in StorageCategory:
            res[cat.value] = self.get_category_dir(cat)
        return res

    def safe_resolve(self, category: StorageCategory, filename: str | Path) -> Path:
        """Resolve a filename inside category directory, preventing path traversal."""
        cat_dir = self.get_category_dir(category).resolve()
        candidate = (cat_dir / filename).resolve()
        try:
            candidate.relative_to(cat_dir)
        except ValueError as exc:
            raise ValueError(f"Path traversal detected: {filename} escapes {cat_dir}") from exc
        return candidate

    def atomic_write(
        self,
        category: StorageCategory,
        filename: str,
        data: bytes | str,
    ) -> tuple[Path, str, int]:
        """Atomically write data to category folder, returning (path, sha256, size)."""
        target = self.safe_resolve(category, filename)
        target.parent.mkdir(parents=True, exist_ok=True)

        raw = data.encode("utf-8") if isinstance(data, str) else data
        size = len(raw)

        # Write to temporary file in same directory for atomic replace
        with tempfile.NamedTemporaryFile(dir=target.parent, delete=False) as tf:
            tf.write(raw)
            tmp_path = Path(tf.name)

        tmp_path.replace(target)
        digest = compute_sha256(target)
        return target, digest, size

    def compute_sha256(self, path: Path) -> str:
        return compute_sha256(path)

    def get_directory_stats(self, category: StorageCategory) -> DirectoryStats:
        """Compute aggregated metrics for a storage category."""
        d = self.get_category_dir(category)
        count = 0
        total_size = 0
        oldest: float | None = None
        newest: float | None = None

        if d.exists():
            for entry in os.scandir(d):
                if entry.is_file() and not entry.name.startswith("."):
                    stat = entry.stat()
                    count += 1
                    total_size += stat.st_size
                    mtime = stat.st_mtime
                    oldest = mtime if oldest is None or mtime < oldest else oldest
                    newest = mtime if newest is None or mtime > newest else newest

        return DirectoryStats(
            category=category.value,
            path=str(d),
            file_count=count,
            total_bytes=total_size,
            oldest_timestamp=oldest,
            newest_timestamp=newest,
        )

    def list_assets(self, category: StorageCategory) -> list[AssetInfo]:
        """List all non-hidden asset files in a category with digests."""
        d = self.get_category_dir(category)
        assets: list[AssetInfo] = []
        if not d.exists():
            return assets

        for entry in os.scandir(d):
            if entry.is_file() and not entry.name.startswith("."):
                stat = entry.stat()
                p = Path(entry.path)
                digest = compute_sha256(p)
                assets.append(
                    AssetInfo(
                        filename=entry.name,
                        relative_path=f"{category.value}/{entry.name}",
                        absolute_path=str(p),
                        size_bytes=stat.st_size,
                        sha256=digest,
                        modified_epoch=stat.st_mtime,
                    )
                )

        assets.sort(key=lambda a: a.modified_epoch, reverse=True)
        return assets

    def delete_asset(self, category: StorageCategory, filename: str) -> bool:
        """Delete an asset file safely within category directory."""
        target = self.safe_resolve(category, filename)
        if target.is_file():
            target.unlink()
            return True
        return False

    def clear_category(self, category: StorageCategory) -> int:
        """Clear all non-hidden files in a category, returning count deleted."""
        d = self.get_category_dir(category)
        deleted = 0
        if d.exists():
            for entry in os.scandir(d):
                if entry.is_file() and not entry.name.startswith("."):
                    Path(entry.path).unlink()
                    deleted += 1
        return deleted
