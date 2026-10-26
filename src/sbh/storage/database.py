"""Minimal database wrapper with two backends.

* ``SQLiteDatabase``: used by the test-suite and local development. Fully exercised.
* ``PostgresDatabase``: the production target. It is a thin psycopg 3 wrapper and has NOT
  been executed in the build environment (no PostgreSQL server was available). The shared
  SQL is written in a portable subset so the same statements are meant to run on both; the
  backend-agnostic integration tests run against PostgreSQL when ``SBH_TEST_POSTGRES_DSN``
  is set. Treat PostgreSQL support as unverified until that has been done.

SQL uses named parameters (``:name``); the PostgreSQL backend rewrites them to ``%(name)s``.
"""

from __future__ import annotations

import re
import sqlite3
from abc import ABC, abstractmethod
from collections.abc import Iterator, Mapping, Sequence
from contextlib import contextmanager
from typing import Any


class Database(ABC):
    dialect: str

    @abstractmethod
    def execute(self, sql: str, params: Mapping[str, Any] | None = None) -> int:
        """Run one statement; return affected row count."""

    @abstractmethod
    def executemany(self, sql: str, rows: Sequence[Mapping[str, Any]]) -> None: ...

    @abstractmethod
    def query_all(self, sql: str, params: Mapping[str, Any] | None = None) -> list[dict[str, Any]]: ...

    def query_one(self, sql: str, params: Mapping[str, Any] | None = None) -> dict[str, Any] | None:
        rows = self.query_all(sql, params)
        return rows[0] if rows else None

    @abstractmethod
    def transaction(self) -> Any:
        """Context manager. Re-entrant: inner blocks join the outermost transaction."""

    @abstractmethod
    def run_script(self, sql: str) -> None:
        """Execute a multi-statement script (used only by the migration runner)."""

    @abstractmethod
    def close(self) -> None: ...


class SQLiteDatabase(Database):
    dialect = "sqlite"

    def __init__(self, path: str = ":memory:") -> None:
        self._conn = sqlite3.connect(path, isolation_level=None, check_same_thread=False)
        self._conn.row_factory = sqlite3.Row
        self._conn.execute("PRAGMA foreign_keys = ON")
        if path != ":memory:":
            self._conn.execute("PRAGMA journal_mode = WAL")
        self._depth = 0

    def execute(self, sql: str, params: Mapping[str, Any] | None = None) -> int:
        return self._conn.execute(sql, params or {}).rowcount

    def executemany(self, sql: str, rows: Sequence[Mapping[str, Any]]) -> None:
        if rows:
            self._conn.executemany(sql, rows)

    def query_all(self, sql: str, params: Mapping[str, Any] | None = None) -> list[dict[str, Any]]:
        return [dict(r) for r in self._conn.execute(sql, params or {}).fetchall()]

    @contextmanager
    def transaction(self) -> Iterator[None]:
        if self._depth > 0:
            self._depth += 1
            try:
                yield
            finally:
                self._depth -= 1
            return
        self._conn.execute("BEGIN IMMEDIATE")
        self._depth = 1
        try:
            yield
        except BaseException:
            self._conn.execute("ROLLBACK")
            self._depth = 0
            raise
        else:
            self._conn.execute("COMMIT")
            self._depth = 0

    def run_script(self, sql: str) -> None:
        self._conn.executescript(sql)

    def rollback_if_open(self) -> None:
        if self._conn.in_transaction:
            self._conn.execute("ROLLBACK")
        self._depth = 0

    def close(self) -> None:
        self._conn.close()


_NAMED = re.compile(r"(?<![:\w]):([A-Za-z_]\w*)")


def to_pyformat(sql: str) -> str:
    """Rewrite ``:name`` placeholders to psycopg's ``%(name)s`` and escape literal percents."""
    return _NAMED.sub(r"%(\1)s", sql.replace("%", "%%"))


class PostgresDatabase(Database):  # pragma: no cover - requires a PostgreSQL server (unverified)
    dialect = "postgresql"

    def __init__(self, dsn: str) -> None:
        try:
            import psycopg
            from psycopg.rows import dict_row
        except ImportError as exc:
            raise RuntimeError("PostgreSQL support needs: pip install 'social-bot-hunter[postgres]'") from exc
        self._conn = psycopg.connect(dsn, autocommit=True, row_factory=dict_row)
        self._depth = 0

    def execute(self, sql: str, params: Mapping[str, Any] | None = None) -> int:
        cur = self._conn.execute(to_pyformat(sql), params or {})
        return cur.rowcount

    def executemany(self, sql: str, rows: Sequence[Mapping[str, Any]]) -> None:
        if rows:
            with self._conn.cursor() as cur:
                cur.executemany(to_pyformat(sql), list(rows))

    def query_all(self, sql: str, params: Mapping[str, Any] | None = None) -> list[dict[str, Any]]:
        return list(self._conn.execute(to_pyformat(sql), params or {}).fetchall())

    @contextmanager
    def transaction(self) -> Iterator[None]:
        if self._depth > 0:
            self._depth += 1
            try:
                yield
            finally:
                self._depth -= 1
            return
        self._conn.execute("BEGIN")
        self._depth = 1
        try:
            yield
        except BaseException:
            self._conn.execute("ROLLBACK")
            self._depth = 0
            raise
        else:
            self._conn.execute("COMMIT")
            self._depth = 0

    def run_script(self, sql: str) -> None:
        self._conn.execute(sql)

    def close(self) -> None:
        self._conn.close()


def connect(url: str) -> Database:
    """Open a database from a URL: ``sqlite:///path``, ``sqlite:///:memory:`` or ``postgresql://...``."""
    if url.startswith("sqlite:///"):
        return SQLiteDatabase(url.removeprefix("sqlite:///") or ":memory:")
    if url.startswith(("postgresql://", "postgres://")):
        return PostgresDatabase(url)
    raise ValueError(f"unsupported database URL scheme: {url.split(':', 1)[0]}")
