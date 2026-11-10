# RUNBOOK-0086: Triaging NDJSON Stream Quarantine Spikes

## Purpose
Investigate sudden spikes in `quarantined` records during NDJSON stream imports.

## Steps
1. Inspect `IngestionBatchSummary.quarantined` sample reasons.
2. If `json_decode_error`, check for partial line truncations or unescaped newline characters.
3. Clean upstream feed with stream sanitizer.
