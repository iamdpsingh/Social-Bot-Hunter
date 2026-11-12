"""Safe database restore engine with safety snapshots and integrity check."""

from __future__ import annotations

import gzip
import shutil
import sqlite3
import time
from dataclasses import asdict, dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from sbh.storage.backup import DatabaseBackupEngine
from sbh.storage.db_verify import verify_backup_integrity, verify_sqlite_database
from sbh.storage.fs import LocalStorageManager, StorageCategory


@dataclass(frozen=True)
class RestoreResult:
    """Outcome of database restore operation."""

    success: bool
    backup_id: str
    target_db: str
    safety_backup_path: str | None
    restored_tables: list[str]
    duration_seconds: float
    error: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


class DatabaseRestoreEngine:
    """Safely restores SQLite databases from backup artifacts."""

    def __init__(self, storage_manager: LocalStorageManager | None = None) -> None:
        self.storage = storage_manager or LocalStorageManager()
        self.backup_engine = DatabaseBackupEngine(self.storage)

    def restore_sqlite(
        self,
        backup_path: Path,
        target_db_path: Path,
        create_safety_backup: bool = True,
    ) -> RestoreResult:
        """Safely restore SQLite database with pre-restore safety snapshot."""
        start_time = time.time()
        backup_id = backup_path.name
        safety_path: Path | None = None

        # 1. Verify backup integrity
        ok, msg = verify_backup_integrity(backup_path)
        if not ok:
            return RestoreResult(
                success=False,
                backup_id=backup_id,
                target_db=str(target_db_path),
                safety_backup_path=None,
                restored_tables=[],
                duration_seconds=round(time.time() - start_time, 3),
                error=f"Integrity check failed: {msg}",
            )

        # 2. Create safety backup of active database if exists
        if create_safety_backup and target_db_path.exists():
            ts = datetime.now(UTC).strftime("%Y%m%d_%H%M%S")
            safety_fn = f"safety_pre_restore_{ts}_{target_db_path.name}"
            safety_path = self.storage.get_category_dir(StorageCategory.BACKUPS) / safety_fn
            try:
                shutil.copy2(target_db_path, safety_path)
            except OSError as exc:
                return RestoreResult(
                    success=False,
                    backup_id=backup_id,
                    target_db=str(target_db_path),
                    safety_backup_path=None,
                    restored_tables=[],
                    duration_seconds=round(time.time() - start_time, 3),
                    error=f"Failed to create safety backup: {exc}",
                )

        # 3. Stage decompressed candidate file if compressed
        is_gz = backup_path.suffix == ".gz" or backup_path.name.endswith(".db.gz")
        staged_path = backup_path

        if is_gz:
            tmp_decompressed = target_db_path.parent / f".tmp_restore_{backup_path.stem}"
            try:
                with gzip.open(backup_path, "rb") as f_in, open(tmp_decompressed, "wb") as f_out:
                    while chunk := f_in.read(65536):
                        f_out.write(chunk)
                staged_path = tmp_decompressed
            except OSError as exc:
                return RestoreResult(
                    success=False,
                    backup_id=backup_id,
                    target_db=str(target_db_path),
                    safety_backup_path=str(safety_path) if safety_path else None,
                    restored_tables=[],
                    duration_seconds=round(time.time() - start_time, 3),
                    error=f"Failed to decompress backup: {exc}",
                )

        # 4. Verify SQLite candidate health before replacing
        check_rep = verify_sqlite_database(staged_path)
        if not check_rep.is_valid:
            if staged_path != backup_path and staged_path.exists():
                staged_path.unlink()
            return RestoreResult(
                success=False,
                backup_id=backup_id,
                target_db=str(target_db_path),
                safety_backup_path=str(safety_path) if safety_path else None,
                restored_tables=[],
                duration_seconds=round(time.time() - start_time, 3),
                error=f"Candidate backup file corrupt: {', '.join(check_rep.errors)}",
            )

        # 5. Remove stale WAL and SHM sidecars to prevent journal corruption
        wal_file = target_db_path.with_name(target_db_path.name + "-wal")
        shm_file = target_db_path.with_name(target_db_path.name + "-shm")
        if wal_file.exists():
            wal_file.unlink()
        if shm_file.exists():
            shm_file.unlink()

        # 6. Atomic swap into target location
        try:
            target_db_path.parent.mkdir(parents=True, exist_ok=True)
            if staged_path != backup_path:
                staged_path.replace(target_db_path)
            else:
                shutil.copy2(backup_path, target_db_path)
        except OSError as exc:
            return RestoreResult(
                success=False,
                backup_id=backup_id,
                target_db=str(target_db_path),
                safety_backup_path=str(safety_path) if safety_path else None,
                restored_tables=[],
                duration_seconds=round(time.time() - start_time, 3),
                error=f"Failed to copy candidate database: {exc}",
            )

        duration = round(time.time() - start_time, 3)
        return RestoreResult(
            success=True,
            backup_id=backup_id,
            target_db=str(target_db_path),
            safety_backup_path=str(safety_path) if safety_path else None,
            restored_tables=check_rep.tables,
            duration_seconds=duration,
            error=None,
        )
