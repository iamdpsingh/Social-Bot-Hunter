# RUNBOOK-0108: Model Card Validation & Recalibration

## Scope & Target
Auditing machine learning model performance metrics against ground-truth benchmarks.

## Operational Procedure
1. Load evaluation dataset: `python -m sbh.detection.ml.evaluation`
2. Verify PR-AUC &ge; 0.85 and F1-score &ge; 0.80.
3. Verify Brier score calibration &le; 0.15.
4. Update `docs/model-card.md` with new evaluation artifacts.
