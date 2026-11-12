"""Integrity verification for SQLite databases and backup manifests."""

from __future__ import annotations

import json
import sqlite3
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

from sbh.storage.fs import compute_sha256


@dataclass(frozen=True)
class DatabaseIntegrityReport:
    """Report detailing SQLite integrity, foreign keys, and table health."""

    is_valid: bool
    integrity_check_passed: bool
    foreign_keys_valid: bool
    table_count: int
    tables: list[str]
    errors: list[str]

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def verify_sqlite_database(db_path: Path) -> DatabaseIntegrityReport:
    """Verify an SQLite database via PRAGMA integrity_check and foreign_keys."""
    if not db_path.exists() or db_path.stat().st_size == 0:
        return DatabaseIntegrityReport(
            is_valid=False,
            integrity_check_passed=False,
            foreign_keys_valid=False,
            table_count=0,
            tables=[],
            errors=["Database file does not exist or is empty"],
        )

    # Check header
    with open(db_path, "rb") as f:
        header = f.read(16)
        if not header.startswith(b"SQLite format 3\x00"):
            return DatabaseIntegrityReport(
                is_valid=False,
                integrity_check_passed=False,
                foreign_keys_valid=False,
                table_count=0,
                tables=[],
                errors=["Invalid SQLite magic header"],
            )

    errors: list[str] = []
    tables: list[str] = []
    integrity_ok = False
    fk_ok = False

    try:
        with sqlite3.connect(f"file:{db_path}?mode=ro", uri=True) as conn:
            cur = conn.cursor()

            # PRAGMA integrity_check
            cur.execute("PRAGMA integrity_check")
            rows = [r[0] for r in cur.fetchall()]
            integrity_ok = len(rows) == 1 and rows[0] == "ok"
            if not integrity_ok:
                errors.extend(rows)

            # PRAGMA foreign_key_check
            cur.execute("PRAGMA foreign_key_check")
            fk_violations = cur.fetchall()
            fk_ok = len(fk_violations) == 0
            if not fk_ok:
                errors.append(f"{len(fk_violations)} foreign key constraint violations detected")

            # Tables list
            cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'")
            tables = [r[0] for r in cur.fetchall()]

    except sqlite3.Error as exc:
        errors.append(f"SQLite error during verification: {exc}")
        return DatabaseIntegrityReport(
            is_valid=False,
            integrity_check_passed=False,
            foreign_keys_valid=False,
            table_count=0,
            tables=[],
            errors=errors,
        )

    is_valid = integrity_ok and fk_ok
    return DatabaseIntegrityReport(
        is_valid=is_valid,
        integrity_check_passed=integrity_ok,
        foreign_keys_valid=fk_ok,
        table_count=len(tables),
        tables=tables,
        errors=errors,
    )


def verify_backup_integrity(
    backup_path: Path,
    metadata_path: Path | None = None,
) -> tuple[bool, str]:
    """Verify cryptographic checksum and metadata match for a backup file."""
    if not backup_path.exists():
        return False, f"Backup file not found: {backup_path}"

    meta_file = metadata_path or backup_path.with_suffix(backup_path.suffix + ".meta.json")
    if not meta_file.exists():
        # Fallback to direct check if no meta file
        return True, "Backup file exists (no metadata file present to verify checksum against)"

    try:
        data = json.loads(meta_file.read_text(encoding="utf-8"))
        expected_sha = data.get("sha256")
        if not expected_sha:
            return False, "Metadata missing 'sha256' field"

        actual_sha = compute_sha256(backup_path)
        if actual_sha != expected_sha:
            return False, f"Checksum mismatch: expected {expected_sha}, got {actual_sha}"

        return True, "Backup integrity and SHA-256 verified successfully"
    except (json.JSONDecodeError, OSError) as exc:
        return False, f"Failed to read metadata file: {exc}"
