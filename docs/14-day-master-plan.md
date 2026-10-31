# Social Bot Hunter — 14-Day Master Implementation Plan & Production Roadmap

**Target Start Date:** 1 November 2026  
**Target Completion Date:** 14 November 2026  
**Commit Velocity Target:** 150+ atomic, production-quality commits per day  
**Target Architecture:** Full-stack (Next.js TypeScript + FastAPI + SQLite/PostgreSQL + NetworkX + Scikit-Learn + Local Virtualenv (.venv) Runtime + GitHub Actions)

---

## 1. Executive Summary & Project Principles

Social Bot Hunter is a production-oriented, cross-platform social media account investigation, bot-risk assessment, and coordinated-network detection platform. It delivers explainable, evidence-backed findings rather than opaque scores or accusations.

### Core Tenets
1. **Evidence-First**: Every assessment presents the exact observed indicators, points breakdown, data coverage percentage, and alternative organic explanations.
2. **Honest Limitations**: The platform explicitly distinguishes between live authorized APIs, permitted dataset imports, and unavailable platform capabilities.
3. **No Synthetic Zeros**: Missing observations are preserved as `null` / `unavailable`, never falsified as zero.
4. **Idempotent Ingestion**: Data pipelines guarantee idempotent writes via SHA-256 content hashing and checkpoint recovery.
5. **High Development Rigor**: Every daily sprint is backed by automated tests, architectural decision records (ADRs), and executable verification.

---

## 2. 14-Day Day-by-Day Implementation Roadmap

### Phase I: Ingestion Hardening, PostgreSQL & REST API (Days 1–3)

#### Day 1 (1 Nov 2026): PostgreSQL Verification, Migrations & Ingestion Resilience
- **Focus**: Validate real PostgreSQL 16 schema against SQLite compatibility layer; test checkpoint recovery and boundary cases.
- **Key Deliverables**:
  - Spin up local and CI PostgreSQL 16 test instances.
  - Run `tests/integration/test_postgres_backend.py` with 100% pass rate.
  - Implement dead-letter / quarantine management CLI commands (`sbh quarantine list/inspect`).
  - Add schema migration rollback verification tests (`db/migrations/rollback/`).
- **Commit Breakdown (150+ commits)**:
  - `feat(storage)`: Connection pooling tuning (psycopg3 pool, max_connections, timeout).
  - `test(postgres)`: Edge case tests for UUID keys, TIMESTAMPTZ formatting, and JSONB index benchmarks.
  - `fix(sql)`: Untyped parameter casting in COALESCE expressions.
  - `data(samples)`: Edge-case CSV datasets (corrupted UTF-8, null characters, extreme follower counts).
  - `docs(status)`: Update PostgreSQL verification records.
- **Acceptance Criteria**: All 205 existing tests pass on PostgreSQL; 0 data-loss on simulated worker interruption.

#### Day 2 (2 Nov 2026): Core FastAPI Service & Authentication Layer
- **Focus**: Expand `services/api` into a production-grade service with JWT authentication, RBAC, and rate limiting.
- **Key Deliverables**:
  - Role-Based Access Control (Admin, Investigator, Auditor, ReadOnly).
  - Token generation, refresh, and revocation in `services/api/auth.py`.
  - Pydantic v2 schemas for all API requests and responses.
  - Structured request logging with `trace_id` and `scan_id` correlation.
- **Commit Breakdown (150+ commits)**:
  - `feat(api)`: Auth router, password hashing (bcrypt), token validation middleware.
  - `feat(api)`: Investigation pagination, sorting, and field-filtering parameters.
  - `test(api)`: 50+ unit tests covering unauthorized access, token expiry, and payload validation.
  - `docs(openapi)`: Export versioned OpenAPI JSON spec (`docs/openapi.json`).
- **Acceptance Criteria**: 100% test coverage on authentication and route protection; OpenAPI 3.1 valid.

#### Day 3 (3 Nov 2026): Asynchronous Job Engine & Background Ingestion
- **Focus**: Background collection task orchestration, scan state transitions, and SSE/WebSocket progress streaming.
- **Key Deliverables**:
  - Asynchronous background worker queue (`sbh.pipeline.worker`).
  - Scan state machine transitions (`pending` -> `running` -> `complete` / `partial` / `failed`).
  - Server-Sent Events (SSE) endpoint (`GET /api/v1/scans/{scan_id}/events`) for live progress updates.
  - Audit logging for every user action and data modification.
- **Commit Breakdown (150+ commits)**:
  - `feat(worker)`: Background thread/process task runner with bounded concurrency.
  - `feat(api)`: SSE streaming handler for scan progress.
  - `test(pipeline)`: Interrupted scan resume tests and retry-with-backoff tests.
  - `perf(ingestion)`: Batch insert optimization (10,000 edges/second).
- **Acceptance Criteria**: Scans can be triggered asynchronously, monitored via SSE, and resumed seamlessly after worker failure.

---

### Phase II: Frontend Investigation Workspace (Days 4–7)

#### Day 4 (4 Nov 2026): Next.js Design System & Overview Page
- **Focus**: Next.js App Router workspace (`apps/dashboard`), design tokens, accessible components, and system overview page.
- **Key Deliverables**:
  - Custom design system (dark/light themes, typography, glassmorphism, responsive navigation).
  - Overview Dashboard (`/`): active investigations, pipeline health, recent scan feed, data coverage cards.
  - Synthetic Demo warning banners and empty-state illustrations.
- **Commit Breakdown (150+ commits)**:
  - `ui(core)`: Button, Badge, Card, Modal, Tooltip, Dropdown, Table components.
  - `ui(overview)`: Investigation summary metrics, platform distribution charts.
  - `feat(dashboard)`: SWR / React Query API client with typed fetchers.
  - `test(e2e)`: Component unit tests with Playwright / Vitest.
- **Acceptance Criteria**: Zero accessibility violations (WCAG 2.1 AA compliant); responsive on mobile and desktop.

#### Day 5 (5 Nov 2026): Account Investigation & Follower/Following Explorer
- **Focus**: Deep-dive account view and interactive relationship browser.
- **Key Deliverables**:
  - Account Profile View (`/investigations/[scan_id]/accounts/[account_id]`): profile metadata, timeline, risk gauges, contributing indicators breakdown.
  - Evidence Inspector: list of exact supporting records, confidence ratings, and limitations.
  - Follower / Following Explorer: high-speed virtualized data table, risk band filtering, search, export to CSV/JSON.
- **Commit Breakdown (150+ commits)**:
  - `ui(investigation)`: Risk radar chart, score breakdown cards, limitation callouts.
  - `ui(relationships)`: Virtualized table for 50,000+ rows, column sorting, search debounce.
  - `feat(export)`: Client-side and server-side CSV/JSON export downloads.
  - `test(ui)`: Filter and pagination test cases.
- **Acceptance Criteria**: Table loads 10,000 items in <100ms; risk breakdown sums match database scores exactly.

#### Day 6 (6 Nov 2026): Interactive Network Explorer (Cytoscape.js)
- **Focus**: Interactive directed graph explorer with layout algorithms, clustering, and node inspection.
- **Key Deliverables**:
  - Cytoscape.js directed graph canvas with node colors, borders, and directional arrows.
  - Layout switchers: Force-directed (cose-bilkent), Hierarchical (dagre), Circular.
  - Interactive click-to-inspect side panel displaying account signals and cluster membership.
  - Accessible table alternative for large graphs (>5,000 nodes) and screen readers.
- **Commit Breakdown (150+ commits)**:
  - `ui(graph)`: Cytoscape canvas container, custom node/edge styles.
  - `feat(graph)`: Subgraph expansion, zoom/pan controls, cluster filtering.
  - `ui(graph)`: Accessible table fallback view with search and sort.
  - `perf(graph)`: WebWorker layout computation for large networks.
- **Acceptance Criteria**: Graph renders smoothly at 60fps for graphs up to 2,000 nodes; table fallback available at all times.

#### Day 7 (7 Nov 2026): Coordinated Activity & Scan Comparison (Diff)
- **Focus**: Multi-scan comparison, coordination signals viewer, and platform settings view.
- **Key Deliverables**:
  - Coordinated Activity View: repeated post content clusters (SimHash), synchronized timing timelines, shared follow hubs.
  - Scan Diff Tool (`/history/diff`): side-by-side comparison showing confirmed additions, confirmed removals, and coverage gaps.
  - Settings & Capabilities View (`/settings`): platform capability status, quota limits, retention configuration.
- **Commit Breakdown (150+ commits)**:
  - `ui(coordination)`: SimHash clusters view, timeline histogram of posting intervals.
  - `ui(diff)`: Diff viewer distinguishing proven removals from unobserved gaps.
  - `ui(settings)`: Platform capability table, retention trigger button.
  - `test(e2e)`: End-to-end user workflow test from import to diff.
- **Acceptance Criteria**: Diff clearly labels unobserved accounts vs confirmed removals; UI fully connected to FastAPI backend.

---

### Phase III: Platform Adapters & Real-World Data (Days 8–10)

#### Day 8 (8 Nov 2026): YouTube Data API v3 & X (Twitter) API v2 Adapters
- **Focus**: Live platform adapters with official OAuth 2.0 / API key authentication and pagination.
- **Key Deliverables**:
  - `sbh.contracts.youtube`: Public profile inspection, channel subscriber/following lists, video metadata.
  - `sbh.contracts.x`: User lookup, public metrics, recent posts, rate-limit backoff.
  - Live profile URL validator (`https://x.com/username`, `https://youtube.com/@channel`).
- **Commit Breakdown (150+ commits)**:
  - `feat(adapter)`: YouTube Data API v3 client with quota calculation.
  - `feat(adapter)`: X API v2 client with bearer token and OAuth 2.0 PKCE.
  - `test(adapter)`: Mock responses and recorded replay fixtures.
  - `docs(matrix)`: Update verification dates and endpoint limitations.
- **Acceptance Criteria**: Live adapters handle 429 Rate Limit gracefully with exponential backoff; unsupported endpoints return explicit `AccessOutcome.UNSUPPORTED`.

#### Day 9 (9 Nov 2026): TikTok & Instagram Graph API Adapters
- **Focus**: Business/Creator API integrations and permitted public data handling.
- **Key Deliverables**:
  - `sbh.contracts.instagram`: Instagram Graph API (Business Discovery endpoint, follower counts, media metrics).
  - `sbh.contracts.tiktok`: TikTok for Developers Display API / Research API contracts.
  - Transparent limitation disclosures for private and non-consented accounts.
- **Commit Breakdown (150+ commits)**:
  - `feat(adapter)`: Instagram Graph API adapter with page token pagination.
  - `feat(adapter)`: TikTok Research API / Commercial API client.
  - `test(adapter)`: Permission-denied error mapping tests.
  - `docs(privacy)`: Platform-specific privacy and data minimisation documentation.
- **Acceptance Criteria**: Adapters never store raw post text or private media; explicit `requires_approval` status tracked.

#### Day 10 (10 Nov 2026): LinkedIn Adapter & Dataset Import Enhancements
- **Focus**: LinkedIn Community Management API and bulk JSON/CSV dataset upload validation.
- **Key Deliverables**:
  - `sbh.contracts.linkedin`: Organization / Member profile lookup adapter.
  - Multi-file ZIP dataset uploader in dashboard and API.
  - Automated format detection (CSV, NDJSON, JSON bundle).
- **Commit Breakdown (150+ commits)**:
  - `feat(adapter)`: LinkedIn API adapter with token refresh handling.
  - `feat(ingestion)`: Multipart streaming upload handler for ZIP/GZ datasets.
  - `test(ingestion)`: Malformed archive security tests (zip bombs, directory traversal).
  - `docs(dictionary)`: Update schema data dictionary.
- **Acceptance Criteria**: Safe handling of multi-megabyte dataset archives; capability registry 100% updated.

---

### Phase IV: Machine Learning, Local Venv Runtime & Hardening (Days 11–14)

#### Day 11 (11 Nov 2026): Machine Learning Models & Metric Calibration
- **Focus**: Train baseline ML models on benchmark data, evaluate against ground truth, and generate model cards.
- **Key Deliverables**:
  - Scikit-Learn pipeline (`sbh.detection.ml`): Logistic Regression, Random Forest, Isolation Forest.
  - Metrics computation: Precision, Recall, F1, PR-AUC, Confusion Matrix, Brier score calibration.
  - Model Card (`docs/model-card.md`) updated with real evaluation results.
  - Versioned model serialization (`data/models/rules_v1.joblib`).
- **Commit Breakdown (150+ commits)**:
  - `feat(ml)`: Feature extraction pipeline with missing-value imputation flags.
  - `feat(ml)`: Random Forest classifier with calibrated probabilities.
  - `test(ml)`: No data leakage verification (cross-validation by cluster).
  - `docs(model_card)`: Comprehensive model card documentation.
- **Acceptance Criteria**: Evaluation computed on isolated test set; PR-AUC and F1 documented with zero leakage.

#### Day 12 (12 Nov 2026): Local Venv Runtime Orchestration, Process Management & Storage Hardening
- **Focus**: Self-contained local virtual environment (`.venv`) orchestration, process lifecycle management (FastAPI + local background queue workers + Next.js frontend), local filesystem snapshot/export management, local SQLite / PostgreSQL database lifecycle, automated backup/restore CLI scripts, and local environment isolation.
- **Key Deliverables**:
  - Multi-service local process supervisor and convenience runner (`scripts/run_local.sh`, Procfile/runner script) coordinating FastAPI API, local worker queue, and Next.js frontend.
  - Local filesystem storage engine for raw dataset snapshots (`data/snapshots/`), trained ML models (`data/models/`), and investigation exports (`data/exports/`) with automated retention and cleanup policies.
  - Local worker process runner with signal handling (`SIGINT`/`SIGTERM`), graceful task completion, and bounded concurrency without cloud queues.
  - Local database backup and restore utility (`sbh db backup` / `sbh db restore`) for SQLite files and local PostgreSQL dumps.
  - Strict local environment validation ensuring `.env` is loaded safely with zero sensitive data leaks in process trees.
- **Commit Breakdown (150+ commits)**:
  - `feat(local)`: Local orchestration script `scripts/run_local.sh` and multi-service process runner.
  - `feat(storage)`: Local directory snapshot and export manager with automated retention enforcement.
  - `feat(cli)`: CLI commands for local database snapshot, dump, and restore (`sbh db backup`, `sbh db restore`).
  - `feat(worker)`: Multi-process local worker queue with file-based / SQLite job dispatch and graceful shutdown.
  - `test(local)`: Tests for local worker concurrency, process crash recovery, snapshot directory retention sweep, and backup integrity.
  - `docs(deployment)`: Step-by-step local virtualenv deployment, process orchestration, and troubleshooting guide.
- **Acceptance Criteria**: Entire platform (FastAPI backend, background worker, and Next.js frontend) runs smoothly in local `.venv` using zero cloud resources or external paid APIs; local backup/restore verified with 100% data integrity.

#### Day 13 (13 Nov 2026): CI/CD Pipelines & Security Audit
- **Focus**: Automated GitHub Actions workflows, container build pipelines, and vulnerability scanning.
- **Key Deliverables**:
  - Multi-stage GitHub Actions CI (`.github/workflows/ci.yml`): lint, typecheck, unit, integration, PostgreSQL, security.
  - Container build & push workflow (`.github/workflows/release.yml`) for Artifact Registry.
  - Automated security scans (Trivy container scan, Bandit static analysis, Trufflehog secret detection).
  - Comprehensive privacy and retention audit sweep.
- **Commit Breakdown (150+ commits)**:
  - `ci(github)`: Matrix testing across Python versions (3.11, 3.12, 3.13).
  - `ci(security)`: Secret scanning, dependency vulnerability audit.
  - `test(security)`: Injection attacks, path traversal, token leakage regression tests.
  - `docs(runbook)`: Incident response and monitoring runbook.
- **Acceptance Criteria**: CI pipeline green; zero high/critical vulnerabilities detected; zero secrets committed.

#### Day 14 (14 Nov 2026): Production Acceptance, End-to-End Verification & Launch
- **Focus**: Full system smoke tests, live profile validation, final documentation sync, and handover.
- **Key Deliverables**:
  - End-to-end integration test from live URL / imported dataset to Cytoscape graph display.
  - Documentation completeness check: README, architecture, platform matrix, data dictionary, runbook.
  - Verification artifact with exact test counts, latency benchmarks, and limitations log.
  - Final tagged release `v1.0.0` on GitHub repository.
- **Commit Breakdown (150+ commits)**:
  - `test(e2e)`: Complete end-to-end verification suite across all 5 platforms.
  - `docs(readme)`: Updated screenshots, quick-start guide, demo video links.
  - `perf(benchmark)`: Database and API query latency report.
  - `chore(release)`: Changelog, release notes, and version tag `v1.0.0`.
- **Acceptance Criteria**: Definition of Done (Specification Section 19) 100% verified; all 14-day milestones met.

---

## 3. High-Frequency Commit Strategy (150+ Commits/Day)

To achieve the requested commit velocity while maintaining enterprise software standards:
1. **Granular Conventional Commits**: Every change is committed atomically using standard prefixes (`feat`, `fix`, `test`, `refactor`, `docs`, `perf`, `infra`, `ui`, `chore`).
2. **Never Break the Build**: Every committed change must compile, format cleanly, and pass the existing test suite.
3. **Commit Cadence Pattern**:
   - Sub-task A: Contract definition & schema (`feat(contract): ...`)
   - Sub-task B: Test fixture & failing test (`test(unit): ...`)
   - Sub-task C: Implementation (`feat(core): ...`)
   - Sub-task D: Edge case handling (`fix(core): ...`)
   - Sub-task E: Integration test (`test(integration): ...`)
   - Sub-task F: Documentation & ADR update (`docs(arch): ...`)
4. **Daily Commit Distribution**:
   - 40 commits: Data contracts, schemas, migrations, and pipeline logic
   - 40 commits: API endpoints, service layer, and workers
   - 40 commits: Frontend UI components, state management, and Cytoscape graphs
   - 30+ commits: Automated tests, benchmark suites, ADRs, and documentation

---

## 4. Verification Checkpoint Table

| Milestone | Target Date | Automated Tests | Critical Verification Evidence |
|---|---|---|---|
| M1: PostgreSQL & REST API | Day 3 (3 Nov) | 250+ passing | PostgreSQL test green, API test green, SSE streaming verified |
| M2: Full Next.js Dashboard | Day 7 (7 Nov) | 300+ passing | Cytoscape graph rendering, accessible tables, diff tool working |
| M3: Live Platform Adapters | Day 10 (10 Nov) | 350+ passing | YouTube/X/TikTok/Instagram adapters verified with rate-limits |
| M4: Production & Local Venv Runtime | Day 14 (14 Nov) | 400+ passing | Local venv runner validated, CI/CD green, zero security findings, v1.0.0 |
