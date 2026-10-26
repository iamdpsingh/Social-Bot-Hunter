"""Shared test helpers. Fixtures are deterministic and clearly synthetic."""

from __future__ import annotations

import csv
import json
import os
import tempfile
import unittest
import uuid
from pathlib import Path
from typing import Any

from sbh.config import Config, load_config
from sbh.fixtures import synthetic
from sbh.storage.database import Database, SQLiteDatabase
from sbh.storage.migrate import apply_migrations

POSTGRES_DSN = os.environ.get("SBH_TEST_POSTGRES_DSN")
T0 = "2026-09-30T12:00:00Z"


def make_db() -> tuple[Database, Any]:
    """In-memory SQLite by default; a throw-away PostgreSQL schema when SBH_TEST_POSTGRES_DSN is set.

    The PostgreSQL branch has NOT been executed in the build environment.
    """
    if POSTGRES_DSN:  # pragma: no cover - needs a server
        from sbh.storage.database import PostgresDatabase

        db = PostgresDatabase(POSTGRES_DSN)
        schema = f"sbh_t_{uuid.uuid4().hex[:12]}"
        db.execute(f"CREATE SCHEMA {schema}")
        db.execute(f"SET search_path TO {schema}")
        apply_migrations(db)

        def cleanup() -> None:
            db.execute(f"DROP SCHEMA {schema} CASCADE")
            db.close()

        return db, cleanup
    db = SQLiteDatabase()
    apply_migrations(db)
    return db, db.close


class DbTestCase(unittest.TestCase):
    cfg: Config

    @classmethod
    def setUpClass(cls) -> None:
        cls.cfg = load_config()

    def setUp(self) -> None:
        self.db, cleanup = make_db()
        self.addCleanup(cleanup)
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.tmp = Path(self._tmp.name)

    def count(self, table: str, where: str = "1=1", **params: Any) -> int:
        row = self.db.query_one(f"SELECT COUNT(*) AS n FROM {table} WHERE {where}", params)
        assert row is not None
        return int(row["n"])


_SYNTH_DIR: Path | None = None


def synthetic_dir() -> Path:
    """Write the default synthetic dataset once per test process."""
    global _SYNTH_DIR
    if _SYNTH_DIR is None:
        tmp = Path(tempfile.mkdtemp(prefix="sbh-synth-"))
        synthetic.write_csv_dir(synthetic.generate(42), tmp / "demo")
        _SYNTH_DIR = tmp / "demo"
    return _SYNTH_DIR


def manifest(**over: Any) -> dict[str, Any]:
    m: dict[str, Any] = {
        "schema_version": "1.0", "dataset_name": "tiny", "platform": "x", "collected_at": T0,
        "source_description": "unit-test fixture", "collection_method": "synthetic",
        "relationship_coverage": {"default": "complete"},
    }
    m.update(over)
    return m


def acct(pid: str, **kw: Any) -> dict[str, Any]:
    row: dict[str, Any] = {"platform": "x", "platform_account_id": pid, "observed_at": "2026-09-30T10:00:00Z",
                           "username": pid, "follower_count": 100, "following_count": 100, "post_count": 500,
                           "has_bio": "true", "has_profile_image": "true", "has_display_name": "true",
                           "account_created_at": "2024-01-01T00:00:00Z"}
    row.update(kw)
    return row


def edge(src: str, dst: str, **kw: Any) -> dict[str, Any]:
    row: dict[str, Any] = {"platform": "x", "source_account_id": src, "target_account_id": dst,
                           "relationship_type": "follows", "observed_at": "2026-09-30T10:00:00Z"}
    row.update(kw)
    return row


def post(cid: str, author: str, ts: str, text: str) -> dict[str, Any]:
    return {"platform": "x", "platform_content_id": cid, "author_account_id": author, "published_at": ts, "text": text}


def write_dir(path: Path, *, man: dict[str, Any], accounts: list[dict[str, Any]] | None = None,
              relationships: list[dict[str, Any]] | None = None, content: list[dict[str, Any]] | None = None) -> Path:
    path.mkdir(parents=True, exist_ok=True)
    (path / "manifest.json").write_text(json.dumps(man), encoding="utf-8")
    for name, rows in (("accounts", accounts), ("relationships", relationships), ("content", content)):
        if not rows:  # absent or empty: no file (an empty CSV would have no header)
            continue
        cols: list[str] = []
        for r in rows:
            cols += [k for k in r if k not in cols]
        with (path / f"{name}.csv").open("w", newline="", encoding="utf-8") as fh:
            w = csv.DictWriter(fh, fieldnames=cols, lineterminator="\n")
            w.writeheader()
            w.writerows(rows)
    return path
