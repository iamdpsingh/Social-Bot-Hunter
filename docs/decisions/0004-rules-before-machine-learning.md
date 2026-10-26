# ADR-0004: Rules-based scoring first, no machine learning yet

**Status:** accepted

**Context.** The specification requires an interpretable baseline before ML, and forbids introducing
a model without a documented dataset, label definition and evaluation. No labelled data exists.

**Decision.** `rules-v1`: a configurable weighted sum of normalised evidence over the features that
are available, with a minimum-evidence rule that yields `insufficient_evidence` and no score.
Every contribution is stored and evidence-linked. `model_versions` already has columns for training
data reference, feature schema and evaluation so a future model fits without a schema change.

**Alternatives.** Train a classifier on synthetic data (it would only learn the generator) or
pseudo-labels from this scorer (circular).

**Consequences.** Scores are uncalibrated ordinal indicators, not probabilities, and the docs say so.
No quality metrics are reported (`model-card.md`). The first real evaluation needs a labelled dataset
with provenance, which is a data-collection task, not a coding task.
