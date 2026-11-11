# RUNBOOK-0096: Diagnosing And Preventing Cross-Validation Data Leakage

## Purpose
Operational guide for engineers and analysts managing diagnosing and preventing cross-validation data leakage.

## Prerequisites
- Local virtual environment active (`source .venv/bin/activate`)
- Python 3.11+ with scikit-learn, joblib, and pytest installed
- Access to benchmark datasets in `data/`

## Standard Operating Procedures
1. **Verification**: Run `python -m sbh ml info` to verify active model version, checksum, and metrics.
2. **Evaluation**: Execute `python -m unittest tests/detection/test_ml_models.py` to assert classification bounds.
3. **Diagnostics**: Check calibration curves via `GET /api/v1/detection/ml/calibration` to ensure ECE remains below 0.05.
4. **Remediation**: If checksum mismatch occurs, reload artifact from trusted repository commit or execute `python scripts/train_baseline_model.py`.

## Escalation
Contact ML Engineering maintainer `dpsingh <dhruvpratapsingh30.official2.o@gmail.com>`.
