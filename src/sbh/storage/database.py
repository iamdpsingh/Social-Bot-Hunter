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
import threading
from abc import ABC, abstractmethod
from collections.abc import Iterator, Mapping, Sequence
from contextlib import contextmanager
from typing import Any

DB_INTEGRITY_ERRORS: tuple[type[Exception], ...]
try:
    import psycopg.errors
    DB_INTEGRITY_ERRORS = (sqlite3.IntegrityError, psycopg.errors.IntegrityError)
except ImportError:
    DB_INTEGRITY_ERRORS = (sqlite3.IntegrityError,)


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


class PostgresPoolDatabase(Database):
    """Thread-safe connection-pooled PostgreSQL database wrapper."""
    dialect = "postgresql"

    def __init__(
        self,
        dsn: str,
        *,
        min_size: int = 1,
        max_size: int = 10,
        timeout: float = 30.0,
        schema: str | None = None,
    ) -> None:
        try:
            from psycopg.rows import dict_row
            from psycopg_pool import ConnectionPool
        except ImportError as exc:
            raise RuntimeError(
                "PostgreSQL connection pooling needs: pip install 'social-bot-hunter[postgres]'"
            ) from exc
        self._dsn = dsn
        self._schema = schema
        self._pool = ConnectionPool(
            dsn,
            min_size=min_size,
            max_size=max_size,
            timeout=timeout,
            open=True,
            kwargs={"autocommit": True, "row_factory": dict_row},
        )
        self._local = threading.local()

    def set_search_path(self, schema: str) -> None:
        """Set the active PostgreSQL search_path across pooled connections."""
        self._schema = schema
        conn = getattr(self._local, "conn", None)
        if conn is not None:
            conn.execute(f"SET search_path TO {schema}")
            conn._sbh_schema = schema

    @contextmanager
    def _get_connection(self) -> Iterator[Any]:
        conn = getattr(self._local, "conn", None)
        if conn is not None:
            yield conn
            return
        with self._pool.connection() as c:
            if self._schema and getattr(c, "_sbh_schema", None) != self._schema:
                c.execute(f"SET search_path TO {self._schema}")
                c._sbh_schema = self._schema  # type: ignore[attr-defined]
            yield c

    def execute(self, sql: str, params: Mapping[str, Any] | None = None) -> int:
        with self._get_connection() as c:
            res = c.execute(to_pyformat(sql), params or {})
            return int(res.rowcount if hasattr(res, "rowcount") and res.rowcount is not None else 0)

    def executemany(self, sql: str, rows: Sequence[Mapping[str, Any]]) -> None:
        if not rows:
            return
        with self._get_connection() as c, c.cursor() as cur:
            cur.executemany(to_pyformat(sql), list(rows))

    def query_all(self, sql: str, params: Mapping[str, Any] | None = None) -> list[dict[str, Any]]:
        with self._get_connection() as c:
            return list(c.execute(to_pyformat(sql), params or {}).fetchall())

    @contextmanager
    def transaction(self) -> Iterator[None]:
        depth = getattr(self._local, "depth", 0)
        if depth > 0:
            self._local.depth += 1
            try:
                yield
            finally:
                self._local.depth -= 1
            return

        with self._get_connection() as conn:
            self._local.conn = conn
            self._local.depth = 1
            conn.execute("BEGIN")
            try:
                yield
            except BaseException:
                conn.execute("ROLLBACK")
                raise
            else:
                conn.execute("COMMIT")
            finally:
                self._local.conn = None
                self._local.depth = 0

    def run_script(self, sql: str) -> None:
        with self._get_connection() as c:
            c.execute(sql)

    def close(self) -> None:
        self._pool.close()


def connect(url: str, *, pool: bool = False) -> Database:
    """Open a database from a URL: ``sqlite:///path``, ``sqlite:///:memory:`` or ``postgresql://...``."""
    if url.startswith("sqlite:///"):
        return SQLiteDatabase(url.removeprefix("sqlite:///") or ":memory:")
    if url.startswith(("postgresql://", "postgres://")):
        if pool:
            return PostgresPoolDatabase(url)
        return PostgresDatabase(url)
    raise ValueError(f"unsupported database URL scheme: {url.split(':', 1)[0]}")
