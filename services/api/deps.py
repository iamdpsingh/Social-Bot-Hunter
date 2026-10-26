"""Dependency injection for FastAPI services."""

import os
from collections.abc import Generator
from pathlib import Path

from sbh.config import Config, load_config
from sbh.storage import Database, SQLiteDatabase, apply_migrations

DEFAULT_DB_PATH = Path("./sbh-dev.sqlite")


def get_config() -> Config:
    return load_config()


def get_db() -> Generator[Database, None, None]:
    db_url = os.environ.get("SBH_DATABASE_URL")
    if db_url and db_url.startswith("postgres"):
        from sbh.storage.database import PostgresDatabase

        db = PostgresDatabase(db_url)
        apply_migrations(db)
        try:
            yield db
        finally:
            db.close()
    else:
        path = db_url.replace("sqlite:///", "") if db_url else str(DEFAULT_DB_PATH)
        db = SQLiteDatabase(path)
        apply_migrations(db)
        try:
            yield db
        finally:
            db.close()
