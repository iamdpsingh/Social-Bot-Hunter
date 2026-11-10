# ADR-0082: Dataset Archive Format Autodetection Heuristics

## Status
Accepted

## Context
Users upload diverse datasets (official Twitter archives, NDJSON firehose dumps, CSV tabular exports) without manual schema specification.

## Decision
Use `DatasetFormatDetector` to recursively inspect manifest files (`manifest.js`, `tweet.js`), file extensions (`.ndjson`, `.csv`), and JSON trees.

## Consequences
Automatic parser dispatch with zero manual configuration required by the investigator.
