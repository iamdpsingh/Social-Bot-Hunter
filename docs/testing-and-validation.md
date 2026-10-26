# Testing and validation

## How to run

```bash
# What was actually run while building this (no install needed):
PYTHONPATH=src python3 -m unittest discover -s tests -t .

# One suite:
PYTHONPATH=src python3 -m unittest discover -s tests/unit -t .

# Intended once dependencies are installed (not run in the build environment):
pip install -e ".[dev]"
python -m pytest -q
```

Tests are `unittest` classes so both runners collect them (ADR-0008). All tests are deterministic
(fixed seeds and clocks). The suite needs only the Python standard library, NetworkX and PyYAML.

## Suites and results

Results from the last full run in the build environment (Python 3.12.3, SQLite 3.45.1):

| Suite | Path | Tests | What it covers |
|---|---|---|---|
| Unit | `tests/unit` | 127 | feature calculations and missing-data handling; score formula, bands, insufficient evidence; evidence ramps; graph directionality, Jaccard against brute force, hub skipping, limits, deadlines, namespaces; temporal sync; scan comparison; cluster logic; fingerprints (banded search vs brute force); validation rules; loader; config validation; retry/backoff; capability registry rules; scan state machine; migrations, checksums, DB constraints; generated-doc and sample-data drift |
| Data quality | `tests/data_quality` | 16 | one test per check in the specification (required fields, identifiers, schema compatibility, duplicates, missingness, timestamps, non-negative counts, direction, referential integrity, freshness, pagination completeness, source consistency, enums, configurable thresholds, nothing silently discarded) |
| Integration | `tests/integration` | 46 (1 skipped) | full pipeline on the synthetic dataset; crash mid-import and resume; rollback; resume equals an uninterrupted run; running/cancelled scans; schema rejection; mostly-invalid input; dirty input with exact quarantine counts; complete vs partial honesty; graph limits degrading to partial; repeated scans and history; JSON vs CSV equivalence; retention and deletion; scale smoke tests |
| Security | `tests/security` | 11 | no raw post text anywhere in the database or logs; SQL-injection strings stored as data; hostile identifiers; oversized and control-character fields; wrongly typed JSON; CSV formula neutralisation; credential-shaped strings in the repository |
| **Total** | | **200** | |

The 1 skipped test is `tests/integration/test_postgres_backend.py`: it runs only when
`SBH_TEST_POSTGRES_DSN` is set, and **has never been run**. The same variable switches the whole
integration suite to PostgreSQL (`tests/support.py:make_db`), also never run.

## What the tests establish, and what they do not

They establish that the code behaves as the methodology and the specification say: missing is never
zero, partial is never reported as complete, every score reconciles to its contributions, a crash
mid-import resumes to the same result as a clean run, a failed batch leaves nothing behind, and
hostile input is handled as data.

They do **not** establish detection quality. See "Model evaluation" below.

## Model evaluation

**None has been done.** There is no labelled real-world dataset, and the system contains no trained
model. No precision, recall, F1, PR-AUC, false-positive rate, confusion matrix or calibration figure
exists, and none should be quoted. The integration tests check that the pipeline finds structure
*planted* in synthetic data; that is a regression check, not an evaluation (see `model-card.md`).

To evaluate properly: build a labelled dataset with documented provenance and label definition; split
so that related accounts and whole coordinated clusters fall on one side only; compute the metrics
above, per platform and account segment; store them in `model_versions.evaluation`; update the model
card.

## Performance observations

Measured on synthetic random graphs in the build sandbox; indicative only, not a claim about real
workloads or about the production environment.

| Test | Input | Result |
|---|---|---|
| Graph stage (build, pair similarity, node metrics, Louvain, cluster detection) | 60,360 edges, 8,011 nodes, 19,635 candidate pairs | 3.7 s, about +65 MB resident memory; the planted 12-account ring was found with no random accounts in it |
| Full import (validate, persist, features, scores, clusters) on SQLite | 25,000 edges, 1,000 accounts | 3.7 s, status `complete` |
| Synthetic demo | 2,375 edges, 1,396 posts, 95 observed accounts | about 0.6 s |

Not measured: PostgreSQL query performance, API latency (no API), worker memory under Cloud Run
limits, graphs of millions of edges. The graph limits (`max_nodes`, `max_edges`, `max_pairs`,
`max_seconds`) exist so that an oversized input fails safely rather than running away. There is no
evidence yet that PySpark or a graph database is needed.

## Fixtures

* `sbh.fixtures.synthetic.generate(seed)`: deterministic synthetic dataset with organic accounts,
  popular hubs, a friend group, an obvious bot ring with two stealthier members, sparse accounts and
  400 stub targets. Labelled `synthetic` in its manifest and in every scan made from it.
  `data/samples/synthetic_demo/` is a committed copy; a test fails if it drifts from the generator.
* `sbh.fixtures.synthetic.make_dirty`: the same dataset with deliberate faults, for quarantine tests.
* `tests/support.py`: tiny dataset builders for focused tests.

## Known gaps

* `ruff`, `mypy` and `pytest` were not available and have not been run. The code is syntax-checked and
  scanned for unused imports only. The first CI run will probably report findings.
* PostgreSQL backend and migration unverified on a real server.
* No tests for the API, authentication, RBAC, export or the dashboard: they do not exist yet.
* No live platform integration tests: no adapters exist.
* No automated test of concurrent workers racing on one scan (the conditional-UPDATE transition is
  tested in a single process).
* No load test at millions of edges; no memory test at Cloud Run limits.
* No dependency lock file (could not be generated offline); dependency ranges are lower bounds.
