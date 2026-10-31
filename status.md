# Project status

Last updated: 2026-10-26 (Pre-Kickoff for 1 November 2026 14-Day Delivery Sprint).

## Summary

The foundation, data ingestion pipeline, rules-based detection engine, graph clustering, REST API foundation, model evaluation baseline, and local virtualenv runtime configurations are implemented and validated: **205 automated tests pass (1 skipped: PostgreSQL without running container)**.

The project is connected to GitHub (`https://github.com/iamdpsingh/Social-Bot-Hunter.git`) and ready for the intensive 14-day delivery sprint commencing 1 November 2026.

## Phase status

| Phase | State | Notes |
|---|---|---|
| 1 Foundation | Done | Structure, contracts, schemas, config, fixtures, docs, `.agents` rules, `.env.example`, `.gitignore`. |
| 2 Data ingestion | Done | CSV/JSON import, validation, normalisation, idempotent persistence, checkpoints, quarantine, data-quality tests. |
| 3 Detection engine | Done | Features, rules scoring, evidence, graph signals, candidate clusters, scan comparison. Evaluated on synthetic benchmark. |
| 4 API and dashboard | In Progress | FastAPI REST API (`services/api`) implemented with health, capabilities, scans, accounts, networks (Cytoscape), imports endpoints and tests. Next.js dashboard structured in `apps/dashboard/`. |
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
| Observations and edges persisted correctly | Yes on SQLite | PostgreSQL schema verified in `0001_init.sql`; live server test ready in CI |
| Repeated ingestion creates no duplicates | Yes | SHA-256 idempotency key; `test_importing_the_same_input_again_changes_nothing` |
| Account risk scores explainable | Yes | Evidence points sum to score; explicit evidence records with source references |
| Candidate networks detected and inspectable | Yes | NetworkX Louvain + Jaccard clustering; API `/api/v1/scans/{id}/networks/graph` Cytoscape format |
| Evidence and coverage for every assessment | Yes | Coverage %, limitations, and contribution records on every assessment |
| Dashboard connected to implemented APIs | Ready | FastAPI backend ready; Next.js workspace in `apps/dashboard/` |
| Historical scans can be inspected | Yes | `sbh scans`, `sbh report`, `sbh diff`, `GET /api/v1/scans/{id}/diff/{id2}` |
| Tests cover critical functionality | Yes | 205 tests across unit, integration, data-quality, security, model evaluation |
| Model evaluation documented where a model is used | Yes | Baseline evaluation in `tests/model_evaluation/test_baseline_eval.py`; Model Card in `docs/model-card.md` |
| Access control, audit logging, retention implemented | Yes | Audit log in database; retention sweep in `sbh.storage.retention`; RBAC in API |
| CI/CD checks run successfully | Ready | Multi-stage workflow written in `.github/workflows/ci.yml` |
| Deployment and recovery instructions | Yes | Local virtualenv runtime guide, process runner, and rollback recovery in `docs/deployment.md` |
| README describes what works and what does not | Yes | Updated with exact verified state |

## Verification evidence

Run in the build environment (Python 3.13, SQLite 3.45.1, NetworkX, PyYAML, FastAPI, Pydantic):

```bash
PYTHONPATH=src:. python3 -m unittest discover -s tests -t .
-> Ran 205 tests, OK (skipped=1)
```

| Suite | Tests |
|---|---|
| unit | 131 |
| data_quality | 16 |
| integration | 46 (1 skipped: PostgreSQL server) |
| security | 11 |
| model_evaluation | 1 |

Also run and verified:
- `python -m sbh demo` (end to end, synthetic data analysis)
- `python -m sbh docs` (generated documentation current)
- `tests/unit/test_api.py` (FastAPI REST endpoints: health, capabilities, scans, Cytoscape graph)
- `tests/model_evaluation/test_baseline_eval.py` (benchmark ground-truth evaluation)

## 14-Day Delivery Plan (1 Nov - 14 Nov 2026)

Full day-by-day roadmap, daily 150+ commit breakdown, and acceptance milestones are documented in [docs/14-day-master-plan.md](docs/14-day-master-plan.md).
