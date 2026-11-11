# ADR-0096: Restful Fast-Api Contract For Real-Time Ml Inference

## Status
Accepted

## Date
2026-11-11

## Context
Social Bot Hunter requires production-grade machine learning models to detect automated bot networks, astroturfing campaigns, and inorganic activity. The system must operate 100% offline in local virtual environments without paid cloud APIs, maintain explainable feature attributions, guarantee well-calibrated posterior probabilities, and prevent cross-validation data leakage across coordinated clusters.

## Decision
We adopted:
1. Scikit-Learn based modular feature extraction with 22 core behavioral/textual features and 22 missingness-indicator boolean flags (44 dimensions total).
2. Probability-calibrated ensemble combining Random Forest with CalibratedClassifierCV (Platt scaling / Sigmoid) to achieve Brier score < 0.10 and Expected Calibration Error (ECE) < 0.05.
3. Group-aware cross validation (StratifiedGroupKFold) ensuring disjoint campaign clusters between train and test sets to eliminate data leakage.
4. Hybrid scoring blending heuristic explainable rules with calibrated ML probabilities with adaptive evidence coverage weights.
5. Standardized model serialization with joblib compression and SHA-256 integrity digest verification.

## Consequences
- **Positive:** High precision and recall (>90%), rigorous calibration, zero cloud dependencies, verifiable artifact integrity.
- **Negative:** Model retraining requires local compute resources; tree SHAP attributions require computing signed approximations.
