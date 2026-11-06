# ADR-0045: Forensic Graph Export Bundle and High-Res Canvas Snapshot

## Status
Accepted

## Context
Legal teams, law enforcement, and compliance officers require downloadable forensic graph evidence in both visual image and machine-readable JSON bundle formats.

## Decision
Implemented `exportGraphPng` (2x high-resolution canvas snapshot) and `exportGraphJson` (Cytoscape JSON bundle with metrics and node metadata), alongside backend endpoint `/scans/{scan_id}/networks/export`.

## Consequences
- Audit-compliant evidence generation ready for incident reports.
- Standard JSON schema readable by Gephi, Cytoscape Desktop, and Python NetworkX.
