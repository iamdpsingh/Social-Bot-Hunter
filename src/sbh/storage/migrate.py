"""Version-controlled migrations: ``db/migrations/NNNN_name.sql`` applied in order.

Applied migrations are recorded with a checksum. Editing an already-applied file is an
error: schema changes go in a new migration.
"""

from __future__ import annotations

import contextlib
import os
import re
from pathlib import Path

from sbh.shared import jsonutil
from sbh.shared.errors import SbhError
from sbh.shared.timeutil import iso_utc, utcnow
from sbh.storage.database import Database, SQLiteDatabase

_NAME = re.compile(r"^(\d{4}_[a-z0-9_]+)\.sql$")


def default_migrations_dir() -> Path:
    env = os.environ.get("SBH_MIGRATIONS_DIR")
    if env:
        return Path(env)
    return Path(__file__).resolve().parents[3] / "db" / "migrations"


def apply_migrations(db: Database, directory: Path | None = None) -> list[str]:
    """Apply pending migrations; return the versions applied in this call."""
    directory = directory or default_migrations_dir()
    db.execute(
        "CREATE TABLE IF NOT EXISTS schema_migrations ("
        "version TEXT PRIMARY KEY, checksum TEXT NOT NULL, applied_at TIMESTAMPTZ NOT NULL)"
    )
    applied = {r["version"]: r["checksum"] for r in db.query_all("SELECT version, checksum FROM schema_migrations")}
    files = sorted(p for p in directory.glob("*.sql") if _NAME.match(p.name))
    if not files:
        raise SbhError(f"no migrations found in {directory}")
    done: list[str] = []
    for path in files:
        version = _NAME.match(path.name).group(1)  # type: ignore[union-attr]
        sql = path.read_text(encoding="utf-8")
        checksum = jsonutil.sha256_hex(sql)
        if version in applied:
            if applied[version] != checksum:
                raise SbhError(
                    f"migration {version} was modified after being applied; "
                    "add a new migration instead of editing an applied one"
                )
            continue
        script = (
            f"BEGIN;\n{sql}\n"
            "INSERT INTO schema_migrations (version, checksum, applied_at) "
            f"VALUES ('{version}', '{checksum}', '{iso_utc(utcnow())}');\nCOMMIT;"
        )
        try:
            db.run_script(script)
        except Exception:
            if isinstance(db, SQLiteDatabase):
                db.rollback_if_open()
            else:  # pragma: no cover - PostgreSQL path unverified
                with contextlib.suppress(Exception):
                    db.execute("ROLLBACK")
            raise
        done.append(version)
    return done
