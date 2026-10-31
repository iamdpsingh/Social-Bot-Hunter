# Workers Architecture

As documented in [ADR-0001](../docs/decisions/0001-single-python-package.md), the core pipeline routines reside in the `sbh` package (`sbh.pipeline`, `sbh.features`, `sbh.detection`, `sbh.graph`).

The subdirectories here provide decoupled entry points for asynchronous queue workers (local multiprocessing, in-process async, or Celery) in self-contained deployments:

- `workers/collection/`: Ingestion worker consuming collection tasks and dataset import jobs.
- `workers/feature_engineering/`: Calculates account-level features.
- `workers/detection/`: Runs the rules engine and graph cluster detection.
- `workers/reporting/`: Generates export bundles and reports.
