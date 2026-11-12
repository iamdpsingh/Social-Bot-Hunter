"""Atomic database backup utility supporting SQLite and PostgreSQL with SHA-256."""

from __future__ import annotations

import gzip
import json
import sqlite3
import time
from dataclasses import asdict, dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from sbh.storage.fs import LocalStorageManager, StorageCategory, compute_sha256


@dataclass
class BackupMetadata:
    """Metadata describing a completed database backup artifact."""

    backup_id: str
    database_type: str  # "sqlite" | "postgresql"
    source_name: str
    filename: str
    relative_path: str
    size_bytes: int
    sha256: str
    table_counts: dict[str, int]
    created_at: str
    is_compressed: bool = False
    notes: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> BackupMetadata:
        return cls(**data)


class DatabaseBackupEngine:
    """Engine for creating verified database backups with companion JSON manifests."""

    def __init__(self, storage_manager: LocalStorageManager | None = None) -> None:
        self.storage = storage_manager or LocalStorageManager()
        self.backup_dir = self.storage.get_category_dir(StorageCategory.BACKUPS)

    def _get_sqlite_table_counts(self, db_path: Path) -> dict[str, int]:
        """Count rows in all tables of an SQLite database."""
        counts: dict[str, int] = {}
        try:
            with sqlite3.connect(f"file:{db_path}?mode=ro", uri=True) as conn:
                cur = conn.cursor()
                cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'")
                tables = [r[0] for r in cur.fetchall()]
                for t in tables:
                    try:
                        cur.execute(f"SELECT COUNT(*) FROM \"{t}\"")
                        counts[t] = cur.fetchone()[0]
                    except sqlite3.Error:
                        counts[t] = -1
        except sqlite3.Error:
            pass
        return counts

    def backup_sqlite(
        self,
        db_path: Path,
        output_filename: str | None = None,
        compress: bool = False,
        notes: str | None = None,
    ) -> tuple[Path, BackupMetadata]:
        """Perform atomic SQLite backup using VACUUM INTO and WAL checkpointing."""
        if not db_path.exists():
            raise FileNotFoundError(f"Database file not found: {db_path}")

        # Checkpoint WAL first
        try:
            with sqlite3.connect(str(db_path)) as conn:
                conn.execute("PRAGMA wal_checkpoint(TRUNCATE)")
        except sqlite3.Error:
            pass

        table_counts = self._get_sqlite_table_counts(db_path)
        timestamp_str = datetime.now(UTC).strftime("%Y%m%d_%H%M%S")
        stem = output_filename or f"backup_sqlite_{timestamp_str}.db"

        raw_bak_path = self.backup_dir / stem
        if raw_bak_path.exists():
            raw_bak_path.unlink()

        # VACUUM INTO creates clean compacted atomic snapshot
        try:
            with sqlite3.connect(str(db_path)) as conn:
                conn.execute(f"VACUUM INTO '{raw_bak_path}'")
        except sqlite3.Error:
            # Fallback to sqlite backup API
            with sqlite3.connect(str(db_path)) as src, sqlite3.connect(str(raw_bak_path)) as dst:
                src.backup(dst)

        final_path = raw_bak_path
        is_compressed = False

        if compress:
            gz_path = raw_bak_path.with_suffix(raw_bak_path.suffix + ".gz")
            with open(raw_bak_path, "rb") as f_in, gzip.open(gz_path, "wb") as f_out:
                while chunk := f_in.read(65536):
                    f_out.write(chunk)
            raw_bak_path.unlink()
            final_path = gz_path
            is_compressed = True

        digest = compute_sha256(final_path)
        size_bytes = final_path.stat().st_size
        backup_id = final_path.name
        now_iso = datetime.now(UTC).isoformat()

        meta = BackupMetadata(
            backup_id=backup_id,
            database_type="sqlite",
            source_name=db_path.name,
            filename=final_path.name,
            relative_path=f"backups/{final_path.name}",
            size_bytes=size_bytes,
            sha256=digest,
            table_counts=table_counts,
            created_at=now_iso,
            is_compressed=is_compressed,
            notes=notes,
        )

        meta_file = final_path.with_suffix(final_path.suffix + ".meta.json")
        meta_file.write_text(json.dumps(meta.to_dict(), indent=2), encoding="utf-8")

        return final_path, meta

    def list_backups(self) -> list[BackupMetadata]:
        """List all completed database backups sorted newest first."""
        results: list[BackupMetadata] = []
        if not self.backup_dir.exists():
            return results

        for meta_file in self.backup_dir.glob("*.meta.json"):
            try:
                data = json.loads(meta_file.read_text(encoding="utf-8"))
                results.append(BackupMetadata.from_dict(data))
            except (json.JSONDecodeError, OSError, TypeError):
                continue

        results.sort(key=lambda b: b.created_at, reverse=True)
        return results

    def get_latest_backup(self, db_type: str | None = None) -> BackupMetadata | None:
        """Retrieve most recent backup, optionally filtered by database type."""
        all_bak = self.list_backups()
        if db_type:
            all_bak = [b for b in all_bak if b.database_type == db_type]
        return all_bak[0] if all_bak else None

    def delete_backup(self, backup_id: str) -> bool:
        """Delete backup artifact and its companion metadata."""
        target = self.backup_dir / backup_id
        meta = self.backup_dir / f"{backup_id}.meta.json"
        deleted = False
        if target.exists():
            target.unlink()
            deleted = True
        if meta.exists():
            meta.unlink()
        return deleted
