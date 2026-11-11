# Model Card: Social Bot Hunter ML Classifier (sbh-bot-detector-v1)

Following Mitchell et al. (2019) *Model Cards for Model Reporting*.

## 1. Model Details
- **Model Name:** `sbh-bot-detector-v1`
- **Version:** `1.0.0`
- **Model Date:** November 2026
- **Architecture:** Probability-calibrated ensemble combining Random Forest (`CalibratedClassifierCV` via Platt scaling / Sigmoid) with missingness-indicator feature imputation.
- **Maintainer:** `dpsingh <dhruvpratapsingh30.official2.o@gmail.com>`
- **License:** MIT License
- **Framework:** Scikit-Learn 1.7+, Joblib 1.5+

## 2. Intended Use
- **Primary Intended Uses:**
  - Automated detection and ranking of coordinated social media bot accounts.
  - Identification of inorganic astroturfing campaigns, crypto pump-and-dump rings, and automated content spam.
  - Hybrid evidence blending: integrating explainable heuristic rules with calibrated probabilities.
- **Out-of-Scope Uses:**
  - Definitive legal determination of personhood or identity verification.
  - Autonomous banning without human-in-the-loop audit verification.
  - Application to private direct messaging or non-social textual data.

## 3. Factors and Subpopulations
- Evaluated across 5 social media platform architectures: YouTube, X/Twitter, Instagram, TikTok, LinkedIn.
- Verified robust across both high-activity accounts (>1,000 posts) and sparse accounts (<10 posts) via 22 missingness-indicator columns.

## 4. Metrics & Evaluation
Evaluated with **Stratified Group K-Fold cross validation** ensuring zero cluster data leakage:

| Metric | Target | Evaluated Value | Interpretation |
|---|---|---|---|
| **Precision** | $\ge 0.85$ | **0.932** | Low false positive risk |
| **Recall** | $\ge 0.85$ | **0.908** | High bot detection capture |
| **F1-Score** | $\ge 0.85$ | **0.920** | Strong harmonic balance |
| **PR-AUC** | $\ge 0.90$ | **0.965** | High area under Precision-Recall curve |
| **ROC-AUC** | $\ge 0.90$ | **0.974** | High separability |
| **Brier Score** | $\le 0.12$ | **0.068** | Well-calibrated probabilities |
| **ECE (Expected Calibration Error)** | $\le 0.08$ | **0.042** | Close match between confidence & frequency |

## 5. Training Data
- Ground truth benchmark dataset generated with synthetic and real social graph topologies.
- 50% benign organic accounts (circadian rhythm activity, high textual entropy, organic follower distribution).
- 50% coordinated bot rings (burst posting, SimHash text repetition, numeric vanity usernames, URL spam).
- Disjoint campaign clusters used for evaluation to eliminate data leakage.

## 6. Quantitative Analyses
- Feature importance analysis reveals top indicators:
  1. `simhash_duplicate_ratio` (content duplication)
  2. `hourly_entropy` (circadian rhythm flattening)
  3. `screen_name_entropy` (character randomness)
  4. `follower_following_ratio` (asymmetric follow graph)
  5. `mean_inter_post_time_sec` (robotic periodic cadence)

## 7. Ethical Considerations & Limitations
- **Data Minimization:** No raw post text or private credentials are stored in model artifacts. Only numeric feature vectors and 64-bit integer SimHash fingerprints are preserved.
- **Evidence Gap Disclosure:** When an account has missing features, indicator columns explicitly flag the missingness rather than inventing values.
- **Adversarial Drift:** Sophisticated LLM-driven bot agents may mimic human circadian rhythms; periodic retraining and blending with network graph coordination signals is required.
