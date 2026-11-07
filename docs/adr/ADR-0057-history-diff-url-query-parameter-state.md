# ADR-0057: URL Query Parameter State Synchronization for Multi-Scan Diffs

## Context
Investigators need to share exact side-by-side scan comparisons with teammates and compliance auditors.

## Decision
The Scan Diff Tool encodes baseline and comparison scan IDs directly into the URL query parameters (`/history/diff?scan_a={id}&scan_b={id}`), allowing reproducible deep-linking.

## Consequences
- Zero-friction sharing of investigation diffs across analysis teams.
