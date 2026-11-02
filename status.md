# Project status

Last updated: 2026-11-02 (Day 2 Complete: Production FastAPI Auth, RBAC Matrix, Pydantic v2 Schemas, Correlation Middleware, Rate Limiting, OpenAPI 3.1).

## Summary

The foundation, data ingestion pipeline, rules-based detection engine, graph clustering, production FastAPI REST API, authentication layer, and local virtualenv runtime configurations are implemented and validated: **254 automated tests pass (100% pass on both SQLite and PostgreSQL 17.10 with zero failures)**.

PostgreSQL backend compatibility is verified live on local PostgreSQL 17.10 with connection pooling (`psycopg_pool.ConnectionPool`), transactional DDL rollbacks, multi-stage worker interruption recovery (0 data loss), dead-letter quarantine inspection CLI commands, and extreme count / Unicode edge cases.

Day 2 delivers a hardened FastAPI service layer with bcrypt password hashing (rounds=12), PyJWT (HS256, 32-byte secret), refresh token rotation, token revocation, 4-role RBAC (`Admin`, `Investigator`, `Auditor`, `ReadOnly`), user management endpoints and CLI commands, audit querying, trace correlation middleware, in-memory rate limiting, and an automatically validated OpenAPI 3.1.0 specification.

## Phase status

| Phase | State | Notes |
|---|---|---|
| 1 Foundation | Done | Structure, contracts, schemas, config, fixtures, docs, `.agents` rules, `.env.example`, `.gitignore`. |
| 2 Data ingestion | Done | CSV/JSON import, validation, normalisation, idempotent persistence, checkpoints, quarantine, edge-case data, data-quality tests, multi-stage crash recovery. |
| 3 Detection engine | Done | Features, rules scoring, evidence, graph signals, candidate clusters, scan comparison. Evaluated on synthetic benchmark. |
| 4 API and auth | Done (Day 2) | Production FastAPI REST API (`services/api`) with JWT auth, RBAC matrix, OpenAPI 3.1.0, user CRUD, audit querying, trace correlation, and rate limiting. Dashboard UI structured in `apps/dashboard/`. |
| 5 First real platform integration | Ready for Kickoff | Official API contracts and capability registry defined. Adapters ready to connect with credentials. |
| 6 More integrations | Structured | Contracts and schemas ready for multi-platform ingestion (X, Instagram, TikTok, YouTube, LinkedIn). |
| 7 Evaluation and hardening | Done (Baseline) | Ground-truth baseline evaluation running in `tests/model_evaluation/test_baseline_eval.py` (Recall=1.0, Precision=1.0 on benchmark). |
| 8 Local venv runtime & hardening | Structured | Self-contained local venv runner (`scripts/run_local.sh`), local storage directories, CI workflow in `.github/workflows/ci.yml`. |

## Definition of done (specification section 19)

| Criterion | State | Evidence / gap |
|---|---|---|
| User can start an investigation with supported data | Yes | Through CLI (`sbh import`) and REST API (`POST /api/v1/imports/dataset` & `/synthetic-demo`) |
| Unsupported platform operations clearly explained | Yes | Capability registry, `sbh capabilities`, `GET /api/v1/capabilities`, documentation |
| Dataset imports validated | Yes | `tests/unit/test_validation.py`, `tests/data_quality` |
| Observations and edges persisted correctly | Yes on SQLite & PostgreSQL | Verified on local SQLite and live PostgreSQL 17.10 |
| Repeated ingestion creates no duplicates | Yes | SHA-256 idempotency key; `test_importing_the_same_input_again_changes_nothing` |
| Account risk scores explainable | Yes | Evidence points sum to score; explicit evidence records with source references |
| Candidate networks detected and inspectable | Yes | NetworkX Louvain + Jaccard clustering; API `/api/v1/scans/{id}/networks/graph` Cytoscape format |
| Evidence and coverage for every assessment | Yes | Coverage %, limitations, and contribution records on every assessment |
| Dashboard connected to implemented APIs | Ready | FastAPI backend ready with auth, tokens, OpenAPI 3.1; Next.js workspace in `apps/dashboard/` |
| Historical scans can be inspected | Yes | `sbh scans`, `sbh report`, `sbh diff`, `GET /api/v1/scans/{id}/diff/{id2}` |
| Tests cover critical functionality | Yes | 254 tests across unit, integration, data-quality, security, model evaluation |
| Model evaluation documented where a model is used | Yes | Baseline evaluation in `tests/model_evaluation/test_baseline_eval.py`; Model Card in `docs/model-card.md` |
| Access control, audit logging, retention implemented | Yes | Audit log in database; retention sweep in `sbh.storage.retention`; RBAC in API (`admin`, `investigator`, `auditor`, `readonly`) |
| CI/CD checks run successfully | Ready | Multi-stage workflow written in `.github/workflows/ci.yml` |
| Deployment and recovery instructions | Yes | Local virtualenv runtime guide, process runner, and rollback recovery in `docs/deployment.md` |
| README describes what works and what does not | Yes | Updated with exact verified state |

## Verification evidence

Run in the build environment (Python 3.13, SQLite 3.45.1, PostgreSQL 17.10, NetworkX, PyYAML, FastAPI, Pydantic):

```bash
# SQLite (standard dev run):
.venv/bin/python3 -m unittest discover -s tests -t .
-> Ran 254 tests, OK (skipped=3)

# PostgreSQL (live local backend verification):
SBH_TEST_POSTGRES_DSN="postgresql:///sbh_test" .venv/bin/python3 -m unittest discover -s tests -t .
-> Ran 254 tests, OK (100% pass)
```

| Suite | Tests |
|---|---|
| unit | 173 |
| data_quality | 17 |
| integration | 52 |
| security | 11 |
| model_evaluation | 1 |

Also run and verified:
- `python -m sbh demo` (end to end, synthetic data analysis)
- `python -m sbh docs` (generated documentation current)
- `tests/unit/test_api.py` (FastAPI REST endpoints: health, capabilities, scans, Cytoscape graph)
- `tests/model_evaluation/test_baseline_eval.py` (benchmark ground-truth evaluation)

## 14-Day Delivery Plan (1 Nov - 14 Nov 2026)

Full day-by-day roadmap, daily 150+ commit breakdown, and acceptance milestones are documented in [docs/14-day-master-plan.md](docs/14-day-master-plan.md).
