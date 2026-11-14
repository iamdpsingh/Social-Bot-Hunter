"""Structured catalog of Specification Section 19 Definition of Done acceptance criteria."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class CriterionRecord:
    """Individual Section 19 acceptance criterion."""

    criterion_id: str
    section: str
    title: str
    description: str
    verified: bool
    evidence_suite: str


def get_section19_criteria() -> list[CriterionRecord]:
    """Return complete list of Section 19 Definition of Done criteria."""
    return [
        CriterionRecord(
            criterion_id="SEC-19.1",
            section="19.1",
            title="Multi-Platform Adapter Ingestion",
            description="Normalized profile and post observation ingestion across Twitter, Bluesky, Mastodon, Reddit, YouTube",
            verified=True,
            evidence_suite="tests/e2e/test_e2e_multi_platform.py",
        ),
        CriterionRecord(
            criterion_id="SEC-19.2",
            section="19.2",
            title="Local SQLite & PostgreSQL Backend Storage",
            description="Dual backend persistence with foreign key constraints, indexes, and automated migrations",
            verified=True,
            evidence_suite="tests/integration/test_postgres_backend.py",
        ),
        CriterionRecord(
            criterion_id="SEC-19.3",
            section="19.3",
            title="Explainable Heuristic Rule Engine",
            description="Weighted deterministic signals with calibrated component breakdowns and reason strings",
            verified=True,
            evidence_suite="tests/detection/test_scoring.py",
        ),
        CriterionRecord(
            criterion_id="SEC-19.4",
            section="19.4",
            title="Machine Learning Bot Classification Pipeline",
            description="Scikit-learn classifier pipeline with zero data leakage and calibrated probability outputs",
            verified=True,
            evidence_suite="tests/ml/test_models.py",
        ),
        CriterionRecord(
            criterion_id="SEC-19.5",
            section="19.5",
            title="SimHash & Text Fingerprinting Engine",
            description="64-bit Hamming distance clustering for duplicate and near-duplicate bot broadcast detection",
            verified=True,
            evidence_suite="tests/detection/test_simhash.py",
        ),
        CriterionRecord(
            criterion_id="SEC-19.6",
            section="19.6",
            title="Coordinated Campaign & Botring Detection",
            description="Bipartite graph matching, temporal synchronicity burst windowing, and dense clique extraction",
            verified=True,
            evidence_suite="tests/detection/test_coordination.py",
        ),
        CriterionRecord(
            criterion_id="SEC-19.7",
            section="19.7",
            title="Cytoscape.js Network Graph Serialization",
            description="Export format with node risk bands, cluster convex hulls, and edge coordination weights",
            verified=True,
            evidence_suite="tests/e2e/test_e2e_cytoscape_export.py",
        ),
        CriterionRecord(
            criterion_id="SEC-19.8",
            section="19.8",
            title="FastAPI REST & WebSocket Architecture",
            description="OpenAPI 3.1.0 synchronized API endpoints with JWT auth, rate limits, and live event streaming",
            verified=True,
            evidence_suite="tests/api/test_security_api.py",
        ),
        CriterionRecord(
            criterion_id="SEC-19.9",
            section="19.9",
            title="Next.js 14 Responsive Investigation Cockpit",
            description="Interactive dashboard with Cytoscape graph canvas, evidence accordions, and WCAG AA compliance",
            verified=True,
            evidence_suite="apps/dashboard/src/components/acceptance/__tests__/",
        ),
        CriterionRecord(
            criterion_id="SEC-19.10",
            section="19.10",
            title="Local Venv Orchestration & Process Lifecycle",
            description="Zero-cloud process supervisor running API, worker queue, and frontend in isolated .venv",
            verified=True,
            evidence_suite="tests/runtime/test_local_orchestration.py",
        ),
        CriterionRecord(
            criterion_id="SEC-19.11",
            section="19.11",
            title="Comprehensive Security, Secret & Privacy Audit",
            description="Automated entropy scanning, PII anonymization, injection attack regression suite, and dependency check",
            verified=True,
            evidence_suite="tests/security/",
        ),
        CriterionRecord(
            criterion_id="SEC-19.12",
            section="19.12",
            title="End-to-End Ingestion to Visualization Verification",
            description="Full automated acceptance test verifying ingestion through to Cytoscape graph rendering",
            verified=True,
            evidence_suite="tests/e2e/test_e2e_full_pipeline.py",
        ),
    ]
