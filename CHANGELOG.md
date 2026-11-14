# Changelog

All notable changes to Social Bot Hunter are documented in this file.
The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2026-11-14

### Production Acceptance, Verification & Release v1.0.0
- **Specification Section 19 Verification**: All 12 Definition of Done criteria verified with 100% automated test coverage (`docs/verification/acceptance-matrix.md`).
- **End-to-End Testing**: Automated pipeline harness from multi-platform mock ingestion to Cytoscape.js network graph export (`tests/e2e/`).
- **Performance Benchmarks**: Micro-benchmark harness with p99 latency SLA verification (`docs/benchmarks/latency-report.md`).
- **Subsystem Diagnostics**: Automated health probes and CLI commands (`sbh doctor`, `sbh benchmark`).
- **Operational Runbooks**: Complete runbook suite RUNBOOK-0101 to RUNBOOK-0110 for production deployment and incident response.
- **Architecture Decision Records**: Complete ADR suite ADR-0098 to ADR-0107 documenting launch decisions.
- **Documentation Completeness**: Production README, system architecture with Mermaid topology, platform capability matrix, and relational data dictionary.

### Previous Milestones Completed (Days 1–13)
- **Day 1**: PostgreSQL 17 Backend & Ingestion Resilience
- **Day 2**: Explainable Heuristic Rule Engine & Signal Attribution
- **Day 3**: Coordinated Inauthentic Behavior (CIB) & SimHash Clustering
- **Day 4**: Next.js 14 Dashboard Scaffolding & Component Architecture
- **Day 5**: Cytoscape.js Network Graph Canvas & Cluster Hull Visualization
- **Day 6**: Investigation Cockpit, Evidence Accordions & Provenance Inspector
- **Day 7**: Follower Explorer, Quota Warnings & Ego-Expansion UX
- **Day 8**: Multi-Platform Adapter Architecture & Verification Contracts
- **Day 9**: Standardized Normalization across X, Bluesky, Mastodon, Reddit, YouTube
- **Day 10**: Ingestion Resilience, Corrupt Archive Handling & Quarantine CLI
- **Day 11**: Machine Learning Classification (Scikit-Learn), Metrics & Model Card
- **Day 12**: Local Venv Runtime Orchestration, Process Supervisor & Storage Hardening
- **Day 13**: CI/CD Pipelines, Multi-Arch Container Images & Comprehensive Security Audit
