# ADR-0053: Automated Data Retention Policies and Cascade Deletion Lifecycle

## Context
Privacy compliance (GDPR/CCPA) requires periodic deletion of investigation snapshots and social media account observations older than designated retention thresholds.

## Decision
We implement `RetentionManager` executing transactional cascade deletions across child tables (`risk_assessments`, `evidence_records`, `relationship_edges`, `scan_jobs`) and pruning orphaned platform accounts while preserving tamper-evident audit logs.

## Consequences
- Strict privacy adherence with verifiable zero data leakage.
- Preserves audit trails of deletion actions for compliance.
