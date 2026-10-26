# ADR-0002: One SQL migration for SQLite and PostgreSQL

**Status:** accepted, with a known verification gap

**Context.** PostgreSQL is the target store. The build environment had no PostgreSQL server and the
specification wants tests that exercise the real schema.

**Decision.** Write `db/migrations/*.sql` in a subset both databases accept: `TEXT` UUID keys,
`TIMESTAMPTZ`, `JSONB`, `BIGINT`, `DOUBLE PRECISION`, `CHECK` constraints, foreign keys,
`ON CONFLICT`. Timestamps are written as fixed-width UTC ISO strings. JSON columns only ever hold an
object or array. Repository SQL uses named parameters, which the PostgreSQL backend rewrites to
`%(name)s`. The test suite runs the real migration on SQLite.

**Alternatives.** (a) Separate SQLite and PostgreSQL schemas: they drift. (b) Mock the database: tests
stop exercising constraints. (c) Require PostgreSQL for all tests: heavier and was impossible here.

**Consequences.** Constraints (including CHECKs for missing-vs-zero and for scored-vs-insufficient) are
tested for real. PostgreSQL-specific features (native UUID, partitioning, GIN indexes on JSONB) are not
used yet. **The PostgreSQL backend has never been run.** `tests/integration/test_postgres_backend.py`
and the backend switch in `tests/support.py` exist for that; they are skipped without
`SBH_TEST_POSTGRES_DSN`. Treat PostgreSQL as unverified until they pass. Known risks to check first:
untyped parameters in a few `COALESCE`/`CASE` expressions, and `executescript`-style multi-statement
migrations through psycopg.
