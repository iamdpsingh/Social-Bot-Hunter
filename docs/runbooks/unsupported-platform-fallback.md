# Runbook: Unsupported Platform Operation Fallback

## Objective
Handle platform API endpoints that are restricted, deprecated, or require enterprise access.

## Behavior
- The pipeline queries `CapabilityRegistry` prior to initiating any live network call.
- If an operation is marked `unsupported` or missing required scopes, the adapter emits an explicit `insufficient_evidence` observation rather than failing the scan.
- Transparent limitations are recorded in `relationship_list_coverage` and exposed via the UI.
