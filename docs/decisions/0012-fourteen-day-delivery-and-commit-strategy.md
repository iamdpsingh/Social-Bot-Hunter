# ADR-0012: 14-Day Delivery Strategy and High-Frequency Commit Protocol

**Status:** accepted

**Context.** The user has commissioned a 14-day intensive production project starting 1 November 2026, targeting a complete, battle-tested platform with a high development velocity (150+ granular, production-grade commits/day, daily verifiable milestones).

**Decision.**
1. Structure the 14 days into 4 clearly demarcated milestone blocks:
   - **Days 1–3 (Core Platform & Ingestion Hardening)**: Complete schema migrations, verify PostgreSQL backend, build FastAPI REST API (`services/api`), validation endpoints, dataset upload, audit trail, OpenAPI docs.
   - **Days 4–7 (Frontend Analytics Workspace)**: Build Next.js dashboard (`apps/dashboard`), Overview, Account Investigation, Follower/Following Explorer, Cytoscape Network Explorer, Coordinated Activity view, Scan History, and Data Sources settings.
   - **Days 8–10 (Platform Adapters & Live Ingestion)**: Implement live platform adapters (X, YouTube, TikTok, Instagram, LinkedIn), OAuth flows, quota throttles, graceful degradation, and live profile verification.
   - **Days 11–14 (ML Hardening, GCP IaC, CI/CD, & Production Acceptance)**: Train baseline ML models on benchmark data, calibrate risk bands, write Terraform IaC, configure GitHub Actions CI/CD pipeline, run end-to-end security audit, and produce final production documentation.
2. **Commit Architecture (150+ Commits/Day)**:
   - Atomic, semantic commits grouped by component (`feat(api)`, `test(storage)`, `docs(adr)`, `ui(network)`, `fix(scoring)`, `perf(graph)`, etc.).
   - Every single commit must leave the codebase in a compilable state with passing tests.
   - Daily automated regression runs ensuring zero regressions across all 200+ unit and integration tests.
3. **Honesty & Verification**:
   - Every daily checkpoint produces a verified progress artifact with test execution outputs, benchmark measurements, and explicit documentation of any platform API limitations.

**Consequences.** Ensures systematic, transparent, high-output delivery without cut corners or fake claims.
