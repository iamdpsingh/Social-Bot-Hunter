# Deployment

**Status: GCP deployment is not implemented.** There is no Terraform, no container image and no
Cloud Run configuration yet (Phase 8). This document records what runs today, the local setup, the
migration and rollback procedure that does apply now, and the planned target so the next phase has a
starting point. Nothing under "Planned" has been built or tested.

## What runs today

A Python library and CLI, run directly. Storage is SQLite for local work and tests. PostgreSQL is the
intended store, supported by the same migration SQL, but **the PostgreSQL backend has never been run**.

## Local setup

```bash
python3 -m venv .venv && . .venv/bin/activate
pip install -e ".[dev]"          # intended; the build was verified with PYTHONPATH=src instead
cp .env.example .env             # then edit; never commit .env

python -m sbh migrate --db ./sbh-dev.sqlite
python -m sbh demo --db ./sbh-dev.sqlite          # synthetic data -> scan -> report
python -m sbh import path/to/dataset --db ./sbh-dev.sqlite
python -m sbh scans --db ./sbh-dev.sqlite
python -m sbh report SCAN_ID --db ./sbh-dev.sqlite
```

Environment (`.env.example`): `SBH_DATABASE_URL` (`sqlite:///path` or `postgresql://...`),
`SBH_CONFIG_PATH` (optional detection config), `SBH_TEST_POSTGRES_DSN` (optional, tests only).

## Database migrations (applies now)

* Files `db/migrations/NNNN_name.sql`, applied in order by `python -m sbh migrate`; each runs in a
  transaction and is recorded in `schema_migrations` with a SHA-256.
* An applied file must not be edited; the runner refuses a changed checksum. Schema changes go in a
  new file.
* **Rollback.** Migrations are forward-only. To undo a bad migration: restore the database from the
  backup taken before it was applied, or write a new migration that reverses it. Take a backup
  (Cloud SQL on-demand backup, or a PostgreSQL dump) before applying any migration to a shared database.
* **Failed migration.** A migration that errors rolls back as a whole and is not recorded; fix it and
  rerun. (Tested on SQLite; PostgreSQL transactional DDL behaviour is unverified here.)
* **Verifying PostgreSQL.** Run the suite with `SBH_TEST_POSTGRES_DSN` set to a disposable database,
  or use the `postgres` job in `.github/workflows/ci.yml`. The tests create and drop their own schema.

## CI

`.github/workflows/ci.yml` runs lint, type check (non-blocking for now), the test suite on Python 3.11
and 3.12, a docs-drift check, the suite against a PostgreSQL service container, `pip-audit` and
`gitleaks`. **It has never run.** Not present yet: container build and vulnerability scan, staging
deploy, smoke tests, production deploy with environment protection.

## Planned GCP target (not built)

The specification's target, with the choices to make when building it:

| Concern | Plan | Open question |
|---|---|---|
| API and workers | Cloud Run services (API) and Cloud Run jobs (workers) | Worker trigger: Cloud Tasks (per-scan, retryable) vs Pub/Sub. Tasks fits "run this scan" better |
| Database | Cloud SQL for PostgreSQL, private IP, automated backups | Size and HA depend on measured load |
| Files | Cloud Storage for imports, snapshots and exports, with versioning and retention rules | Nothing writes to it yet |
| Scheduling | Cloud Scheduler for scheduled scans | Needs live adapters first |
| Secrets | Secret Manager; no secrets in images, env files or Terraform state | |
| Identity | One service account per service, least privilege; GitHub deploys via Workload Identity Federation (no long-lived keys) | |
| Observability | Cloud Logging (the logs are already JSON with `scan_id`) and Cloud Monitoring alerts | Alert definitions: see `monitoring-runbook.md` |
| Environments | Separate dev, staging and production projects or configurations | |
| Cost | Budget alerts per project | |
| IaC | Terraform, with project IDs and environment values as variables, never hard-coded | |
| Teardown | `terraform destroy` per environment, after exporting or deleting data | Document when built |

Before any production data is stored, the following must exist: authentication and RBAC (Phase 4),
Cloud SQL not reachable from the public internet, a retention period agreed with the data owner, and a
verified PostgreSQL run of the test suite.
