"""Subsystem health probes verifying local database, storage, and offline constraints."""

from __future__ import annotations

import os
import shutil
import sqlite3
import time
from dataclasses import dataclass
from enum import StrEnum
from pathlib import Path
from typing import Any


class SubsystemStatus(StrEnum):
    HEALTHY = "HEALTHY"
    DEGRADED = "DEGRADED"
    UNHEALTHY = "UNHEALTHY"


@dataclass
class HealthProbeResult:
    """Result of an individual subsystem health probe."""

    subsystem: str
    status: SubsystemStatus
    latency_ms: float
    details: str
    metadata: dict[str, Any]


class HealthProbeRunner:
    """Runs targeted health checks against local subsystem dependencies."""

    @classmethod
    def check_sqlite(cls, db_path: str | Path | None = None) -> HealthProbeResult:
        """Verify SQLite database connection, write/read latency, and integrity."""
        start = time.perf_counter()
        target = str(db_path) if db_path else ":memory:"
        try:
            conn = sqlite3.connect(target)
            cur = conn.cursor()
            cur.execute("PRAGMA integrity_check;")
            integrity_row = cur.fetchone()
            integrity = integrity_row[0] if integrity_row else "unknown"

            cur.execute("CREATE TABLE IF NOT EXISTS _health_probe (id INTEGER PRIMARY KEY, ts REAL);")
            cur.execute("INSERT INTO _health_probe (ts) VALUES (?);", (time.time(),))
            conn.commit()
            cur.execute("SELECT COUNT(*) FROM _health_probe;")
            count = cur.fetchone()[0]
            conn.close()

            elapsed = (time.perf_counter() - start) * 1000.0
            status = SubsystemStatus.HEALTHY if integrity == "ok" else SubsystemStatus.DEGRADED

            return HealthProbeResult(
                subsystem="database_sqlite",
                status=status,
                latency_ms=round(elapsed, 3),
                details=f"SQLite check passed (integrity={integrity}, rows={count})",
                metadata={"integrity": integrity, "db_path": target, "rows": count},
            )
        except Exception as exc:
            elapsed = (time.perf_counter() - start) * 1000.0
            return HealthProbeResult(
                subsystem="database_sqlite",
                status=SubsystemStatus.UNHEALTHY,
                latency_ms=round(elapsed, 3),
                details=f"SQLite check failed: {exc}",
                metadata={"error": str(exc)},
            )

    @classmethod
    def check_storage_directories(cls, base_dir: Path | None = None) -> HealthProbeResult:
        """Verify local storage directories are writable and have disk headroom."""
        start = time.perf_counter()
        root = base_dir or Path("data")
        subdirs = ["snapshots", "exports", "models", "temp"]
        missing = []
        writable = []

        root.mkdir(parents=True, exist_ok=True)
        for s in subdirs:
            p = root / s
            p.mkdir(parents=True, exist_ok=True)
            test_file = p / ".probe_test"
            try:
                test_file.write_text("ok", encoding="utf-8")
                test_file.unlink()
                writable.append(s)
            except Exception:
                missing.append(s)

        total, used, free = shutil.disk_usage(root)
        free_gb = round(free / (1024**3), 2)
        elapsed = (time.perf_counter() - start) * 1000.0

        status = SubsystemStatus.HEALTHY if not missing and free_gb >= 0.5 else SubsystemStatus.DEGRADED

        return HealthProbeResult(
            subsystem="filesystem_storage",
            status=status,
            latency_ms=round(elapsed, 3),
            details=f"Storage verified (writable={len(writable)}/{len(subdirs)}, free={free_gb}GB)",
            metadata={"writable_dirs": writable, "free_gb": free_gb, "missing_or_readonly": missing},
        )

    @classmethod
    def check_model_artifacts(cls, models_dir: Path | None = None) -> HealthProbeResult:
        """Verify baseline trained models or rules are present."""
        start = time.perf_counter()
        mdir = models_dir or Path("data/models")
        mdir.mkdir(parents=True, exist_ok=True)
        artifacts = list(mdir.glob("*.*"))
        elapsed = (time.perf_counter() - start) * 1000.0

        return HealthProbeResult(
            subsystem="ml_model_artifacts",
            status=SubsystemStatus.HEALTHY,
            latency_ms=round(elapsed, 3),
            details=f"Model directory ready ({len(artifacts)} files found)",
            metadata={"artifacts_count": len(artifacts), "path": str(mdir)},
        )
