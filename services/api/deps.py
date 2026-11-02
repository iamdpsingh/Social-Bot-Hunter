"""Dependency injection for FastAPI services."""

from __future__ import annotations

import os
from collections.abc import Generator
from pathlib import Path

from sbh.config import Config, load_config
from sbh.storage import Database, SQLiteDatabase, apply_migrations

DEFAULT_DB_PATH = Path("./sbh-dev.sqlite")
_pg_pool: Database | None = None


def get_config() -> Config:
    return load_config()


def get_db() -> Generator[Database, None, None]:
    db_url = os.environ.get("SBH_DATABASE_URL")
    if db_url and db_url.startswith("postgres"):
        global _pg_pool
        from sbh.storage.database import PostgresPoolDatabase

        if _pg_pool is None:
            _pg_pool = PostgresPoolDatabase(db_url)
            apply_migrations(_pg_pool)
        yield _pg_pool
    else:
        path = db_url.replace("sqlite:///", "") if db_url else str(DEFAULT_DB_PATH)
        db = SQLiteDatabase(path)
        apply_migrations(db)
        try:
            yield db
        finally:
            db.close()
