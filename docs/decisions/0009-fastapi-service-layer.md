# ADR-0009: FastAPI for REST API and Async Scans

**Status:** accepted

**Context.** The pipeline and CLI exist, but users and the frontend dashboard need a versioned HTTP API (`/api/v1`) for account investigations, scan lifecycle tracking, result retrieval, capability discovery, and evidence inspection.

**Decision.** Build the API service in `services/api` (and installable `sbh.api`) using FastAPI with Pydantic v2 schemas.
1. All endpoints are versioned under `/api/v1`.
2. Heavy operations (dataset import, graph analysis, platform collection) run asynchronously via background workers or Cloud Tasks, returning a `scan_id` with `202 Accepted` and polling/SSE status. Synchronous request handlers never block on long-running graph analysis.
3. Authentication uses short-lived JWTs with role-based access control (Admin, Investigator, Auditor, ReadOnly).
4. Auto-generate and validate the OpenAPI specification (`docs/openapi.json`) in CI.
5. Reuse existing `sbh.storage` repositories and `sbh.contracts` capability models directly to prevent logic duplication.

**Alternatives.**
- Flask / Django: Heavier or lacks native async and Pydantic validation.
- GraphQL: Higher complexity for client caching and graph queries without immediate justification.

**Consequences.** Clean contract between backend and dashboard. API schemas remain strictly typed and validated against database constraints.
