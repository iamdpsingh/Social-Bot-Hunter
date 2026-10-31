# Social Bot Hunter

An investigation tool that looks at social media accounts and the relationships between them, and
reports **suspicious indicators and candidate coordinated groups, with the evidence, the data
coverage and the alternative explanations next to each result.**

It does not tell you that an account *is* a bot. A high score means a strong combination of suspicious
indicators was observed, and nothing more. It never takes action against an account.

> **Status: Core Pipeline, REST API & Evaluation Tested.** The ingestion pipeline, explainable scoring engine, graph clustering, FastAPI REST API, model evaluation baseline, and local virtualenv runtime are implemented and verified with 205 automated tests. Frontend Next.js dashboard workspace and live authorized platform adapters kick off 1 November 2026 for a 14-day delivery sprint.

## What works and what does not

| Component | State |
|---|---|
| Import CSV/JSON datasets with validation, quarantine and provenance | Works, tested |
| Idempotent, restartable ingestion (crash, resume, rollback) | Works, tested |
| Explainable per-account risk score, or "insufficient evidence" | Works, tested on SQLite |
| Candidate coordinated-network detection with evidence and alternative explanations | Works, tested on synthetic data |
| Compare two scans without confusing missing data for change | Works, tested |
| Capability registry saying what each platform can and cannot provide | Works, exposed via CLI and REST API |
| Scan deletion and retention sweep, audit trail | Works, tested |
| FastAPI REST API (`services/api`) & OpenAPI docs | Works, tested (`tests/unit/test_api.py`) |
| Model evaluation against synthetic ground truth | Works, tested (`tests/model_evaluation/`) |
| GitHub Actions CI/CD workflow | Structured in `.github/workflows/ci.yml` |
| Local Venv Runtime & Process Management | Implemented in `scripts/run_local.sh` & `docs/deployment.md` |
| Next.js Investigation Dashboard | Structured in `apps/dashboard/` (Days 4–7) |
| Live platform adapters (Instagram, X, TikTok, YouTube, LinkedIn) | Structured in `sbh.contracts` (Days 8–10) |
| PostgreSQL backend | Schema verified; integration test passes with live container |
| Detection accuracy on real accounts | Unknown. Heuristics calibrated on benchmark data; ground-truth evaluation in progress |

No architecture can guarantee complete follower/following access on every network. Live access depends on each platform's official API and approvals. Dataset import works for every platform today.

- Details: [docs/status.md](docs/status.md)
- 14-Day Delivery Roadmap: [docs/14-day-master-plan.md](docs/14-day-master-plan.md)

## Quick start

Needs Python 3.11+, NetworkX and PyYAML. No server is required.

```bash
# verified route (no install):
PYTHONPATH=src python3 -m sbh demo --db ./sbh-dev.sqlite

# intended route (not run while building):
pip install -e ".[dev]" && python -m sbh demo --db ./sbh-dev.sqlite
```

`demo` generates a **synthetic** dataset (invented accounts, clearly labelled), imports it, analyses it
and prints a report. An excerpt of the real output:

```
Scan 180b7442-...  *** SYNTHETIC DEMO DATA: no real accounts ***
  platform=x status=partial collection_completeness=partial config=rules-v1
  partial because: relationship collection completeness is 'partial'

Account risk (heuristic indicators, not proof of automation). Highest first:
  r004   89.8  strong_combination_of_indicators  coverage=95%  top: duplicate_content_ratio=1 (+21.6), ...
  ...
Candidate clusters (structure alone is NOT evidence of coordination):
  10 accounts  signal_strength=high  confidence=moderate  review=unreviewed
    content_duplication: present   member_risk: present   temporal_synchrony: present
  8 accounts   signal_strength=low   confidence=moderate  review=unreviewed
    content_duplication: absent    member_risk: absent    temporal_synchrony: absent
    alternative: Members follow each other mutually, which is typical of friends, teams or organisations.
```

The second cluster is a planted friend group. It overlaps structurally with a bot ring but is kept at
`low` strength, because overlap alone is common in organic communities.
Those results come from synthetic data built to contain exactly this. They show the code works as
designed, not that it is accurate on real accounts.

## Commands

```bash
python -m sbh migrate              # apply migrations, sync the capability registry
python -m sbh import PATH          # import a dataset directory or JSON bundle, then analyse
python -m sbh scans                # list scans
python -m sbh report SCAN_ID       # scores, evidence, clusters, limitations
python -m sbh diff SCAN_A SCAN_B   # relationship changes, separating confirmed from unconfirmed
python -m sbh capabilities         # what each platform operation supports (--markdown for a table)
python -m sbh generate-demo --out DIR --seed 42
python -m sbh delete-scan SCAN_ID  # delete a scan and everything derived from it
python -m sbh retention-sweep --days 90
python -m sbh docs [--write]       # check or refresh the generated tables in docs/
```

Global options: `--db URL_OR_PATH` (or `SBH_DATABASE_URL`), `--config FILE`, `-v` (JSON logs).
The import format is described in [docs/data-dictionary.md](docs/data-dictionary.md); a complete
example is in `data/samples/synthetic_demo/`.

## Running the tests

```bash
PYTHONPATH=src python3 -m unittest discover -s tests -t .      # 200 tests, about 20 s
```

See [docs/testing-and-validation.md](docs/testing-and-validation.md) for what they cover and what they
do not.

## How it is built

```
CSV/JSON dataset -> validate + quarantine -> batched, checkpointed writes -> features
                 -> explainable score + evidence -> graph signals -> candidate clusters
```

* `src/sbh/schemas`: import format, validation, normalisation.
* `src/sbh/storage` and `db/migrations`: SQL repositories and versioned migrations (one SQL file for SQLite and PostgreSQL).
* `src/sbh/features`, `detection`, `graph`: pure analysis code.
* `src/sbh/pipeline`: scan orchestration, state machine, resume.
* `src/sbh/contracts`: platform capability registry and adapter contract.
* `src/sbh/resources/detection.v1.yaml`: every weight and threshold.

Architecture and decisions: [docs/architecture.md](docs/architecture.md), [docs/decisions/](docs/decisions/).

## Principles the code enforces

* Missing is not zero. Unavailable features have no value and a reason; the database rejects the alternative.
* Partial is not complete. A scan is `complete` only if nothing was rejected, nothing skipped, and every relationship list is known to be whole.
* No score without enough evidence. Otherwise: `insufficient_evidence`.
* Every score reconciles to per-feature contributions, each tied to evidence records.
* Raw post text is never stored, only fingerprints.
* Nothing invented: no endpoints, scopes or permissions that were not checked.
* A pipeline failure is never reported as a finding about an account.

## Documentation

| | |
|---|---|
| [status](docs/status.md) | What is done, what is not, evidence, next steps |
| [architecture](docs/architecture.md) | Components, data flow, failure handling, trade-offs |
| [detection methodology](docs/detection-methodology.md) | Features, score formula, graph signals, limitations |
| [model card](docs/model-card.md) | Intended use, data, evaluation (none yet), limitations |
| [platform access matrix](docs/platform-access-matrix.md) | What each platform operation supports and how far verified |
| [data dictionary](docs/data-dictionary.md) | Import format and every table |
| [privacy and retention](docs/privacy-and-retention.md) | What is stored, deletion, access control status |
| [testing and validation](docs/testing-and-validation.md) | Suites, results, performance, gaps |
| [deployment](docs/deployment.md) | Local virtualenv setup, migrations, rollback, and process runner |
| [monitoring runbook](docs/monitoring-runbook.md) | Failure categories and recovery |
| [CONTRIBUTING](CONTRIBUTING.md) | How to change things safely |

## Responsible use

For analysis and investigation. Do not use it for harassment, doxxing, mass targeting or automated
punitive action, and do not use it to get around privacy settings or platform access controls. Whoever
imports a dataset is responsible for having the right to use it.
