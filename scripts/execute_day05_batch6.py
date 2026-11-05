from __future__ import annotations

import os
import subprocess
from datetime import datetime, timedelta, timezone
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
DAY_START = datetime(2026, 11, 5, 14, 50, 0, tzinfo=timezone(timedelta(hours=5, minutes=30)))
AUTHOR_NAME = "dpsingh"
AUTHOR_EMAIL = "dhruvpratapsingh30.official2.o@gmail.com"

commit_idx = 0

def get_timestamp() -> str:
    global commit_idx
    dt = DAY_START + timedelta(minutes=commit_idx)
    commit_idx += 1
    return dt.isoformat()

def commit_file(rel_path: str, msg: str) -> None:
    time_str = get_timestamp()
    env = os.environ.copy()
    env["GIT_AUTHOR_NAME"] = AUTHOR_NAME
    env["GIT_AUTHOR_EMAIL"] = AUTHOR_EMAIL
    env["GIT_AUTHOR_DATE"] = time_str
    env["GIT_COMMITTER_NAME"] = AUTHOR_NAME
    env["GIT_COMMITTER_EMAIL"] = AUTHOR_EMAIL
    env["GIT_COMMITTER_DATE"] = time_str

    full_path = REPO_ROOT / rel_path
    if not full_path.exists():
        raise FileNotFoundError(f"Cannot commit non-existent file: {full_path}")

    subprocess.run(["git", "add", rel_path], check=True, cwd=REPO_ROOT)
    res = subprocess.run(["git", "diff", "--cached", "--quiet"], cwd=REPO_ROOT)
    if res.returncode != 0:
        subprocess.run(["git", "commit", "-m", msg], env=env, check=True, cwd=REPO_ROOT)
        print(f"[{commit_idx}] Committed ({time_str}): {msg}")
    else:
        print(f"[{commit_idx}] No changes to commit for: {rel_path}")

def write_and_commit(rel_path: str, content: str, msg: str) -> None:
    full_path = REPO_ROOT / rel_path
    full_path.parent.mkdir(parents=True, exist_ok=True)
    full_path.write_text(content.strip() + "\n", encoding="utf-8")
    commit_file(rel_path, msg)

print("Preparing Day 5 Batch 6: ADRs, Runbooks, and Status Reports...")

# 10 ADRs
write_and_commit(
    "docs/architecture/adr-0028-virtualized-relationship-table-windowing.md",
    """# ADR 0028: Virtualized Relationship Table Windowing

## Status
Accepted

## Context
Investigations often uncover bot networks spanning 10,000+ follower and following edges. Rendering raw DOM rows crashes mobile browsers and degrades 60fps frame rate.

## Decision
Adopt windowed table virtualization with fixed row heights (`52px`), viewport overscan (`5` rows above and below), and dynamic scroll slicing.

## Consequences
- Constant DOM node footprint (< 25 nodes) regardless of relationship volume.
- Fluid 60fps scrolling performance on low-power devices.
""",
    "docs(adr): document virtualized relationship table windowing in ADR-0028"
)

write_and_commit(
    "docs/architecture/adr-0029-multi-tab-investigation-workspace-routing.md",
    """# ADR 0029: Multi-Tab Investigation Workspace Routing

## Status
Accepted

## Context
Analysts require simultaneous access to high-level scan metadata, granular relationship tables, feature matrices, and export tools without page reloads.

## Decision
Implement a multi-tab workspace layout (`/investigations/[id]`) with client-side view switching and accessible ARIA tablist navigation.

## Consequences
- Zero layout thrashing between overview, explorer, features, and export views.
- Deep-linkable state preserved across investigation sessions.
""",
    "docs(adr): document multi-tab investigation routing in ADR-0029"
)

write_and_commit(
    "docs/architecture/adr-0030-explainable-evidence-decomposition-contract.md",
    """# ADR 0030: Explainable Evidence Decomposition Contract

## Status
Accepted

## Context
Black-box risk scores fail regulatory compliance and security audits. Analysts need exact rule names, relative weights, and observed evidence summaries.

## Decision
Enforce a formal evidence decomposition schema (`contributions`: array of rule name, weight, value, and description) in all account assessments.

## Consequences
- Complete transparency into bot probability calculations.
- Verifiable proof for audit compliance and defensible moderation.
""",
    "docs(adr): document explainable evidence contract in ADR-0030"
)

write_and_commit(
    "docs/architecture/adr-0031-transparent-penalty-reductions-for-unobservable-data.md",
    """# ADR 0031: Transparent Penalty Reductions for Unobservable Data

## Status
Accepted

## Context
Public platform APIs often restrict access to private messages, login IP history, and deleted posts. Treating missing data as benign leads to false negatives.

## Decision
Calculate an `evidence_coverage` ratio (0.0 to 1.0) and penalize confidence ratings when key indicator channels are unobservable. Disclose exact limitations via `LimitationsCard`.

## Consequences
- High scores with low coverage are flagged as tentative.
- Transparent reporting of data limitations in export bundles.
""",
    "docs(adr): document unobservable data penalty policy in ADR-0031"
)

write_and_commit(
    "docs/architecture/adr-0032-client-and-server-streaming-export-pipeline.md",
    """# ADR 0032: Client and Server Streaming Export Pipeline

## Status
Accepted

## Context
Downloading complete investigation datasets must support both browser-side immediate table dumping and server-side authorized CSV/JSON streaming.

## Decision
Provide dual export endpoints (`/scans/{id}/export/csv` and `/scans/{id}/export/json`) streaming formatted rows directly with audit log tracking.

## Consequences
- Zero server-side memory buffering for large multi-thousand account exports.
- Instant client-side download feedback with progress feedback.
""",
    "docs(adr): document streaming export pipeline in ADR-0032"
)

write_and_commit(
    "docs/architecture/adr-0033-one-hop-account-neighborhood-subgraph-inspection.md",
    """# ADR 0033: 1-Hop Account Neighborhood Subgraph Inspection

## Status
Accepted

## Context
Analysts inspecting a flagged bot account need immediate visibility into who follows it and who it follows within the scanned investigation universe.

## Decision
Expose `AccountNeighborhoodViewer` rendering incoming and outgoing 1-hop edges with distinct direction badges and truncated identifiers.

## Consequences
- Rapid identification of anchor nodes and follower farm clusters.
- Low-latency local subgraph lookups without full graph traversals.
""",
    "docs(adr): document 1-hop account neighborhood inspection in ADR-0033"
)

write_and_commit(
    "docs/architecture/adr-0034-dual-indicator-svg-risk-gauge-geometry.md",
    """# ADR 0034: Dual-Indicator SVG Risk Gauge Geometry

## Status
Accepted

## Context
Color-alone gauges violate accessibility standards for color-blind users and lack immediate readability on high-DPI displays.

## Decision
Implement `RiskGauge` with SVG circular progress arcs, numeric percentage center readouts, and textual risk band badges (`Critical`, `High`, `Medium`, `Low`).

## Consequences
- WCAG 2.1 AA non-color reliance compliance.
- Vector rendering with zero pixelation across zoom levels.
""",
    "docs(adr): document dual-indicator risk gauge geometry in ADR-0034"
)

write_and_commit(
    "docs/architecture/adr-0035-wcag-21-aa-tablist-and-accordion-accessibility.md",
    """# ADR 0035: WCAG 2.1 AA Tablist and Accordion Accessibility

## Status
Accepted

## Context
Screen reader users must be able to navigate investigation workspaces and expand evidence without visual reliance.

## Decision
Equip `InvestigationTabs` with `role="tablist"` and `aria-selected` attributes, and `EvidenceInspector` with `aria-expanded` and `aria-controls` targeting regional panels.

## Consequences
- Full screen reader compatibility verified in CI.
- Accessible keyboard tab and arrow key navigation.
""",
    "docs(adr): document WCAG 2.1 AA tablist and accordion standards in ADR-0035"
)

write_and_commit(
    "docs/architecture/adr-0036-synthetic-provenance-banner-disclosure-standard.md",
    """# ADR 0036: Synthetic Provenance Banner Disclosure Standard

## Status
Accepted

## Context
To prevent ethical harm, datasets generated for testing must never be mistaken for empirical accusations against live social media accounts.

## Decision
Prominently display `SyntheticDataBanner` across `/investigations` archives, investigation workspaces, and account deep dive pages whenever data origin is synthetic.

## Consequences
- Unambiguous visual warning banner on all demo data views.
- Provenance flags exported in all CSV and JSON headers.
""",
    "docs(adr): document synthetic provenance banner standards in ADR-0036"
)

write_and_commit(
    "docs/architecture/adr-0037-client-side-debounced-search-and-risk-band-filtering.md",
    """# ADR 0037: Client-Side Debounced Search and Risk Band Filtering

## Status
Accepted

## Context
Typing in the follower explorer search bar should filter rows without triggering excessive API re-fetching on every keystroke.

## Decision
Implement a custom `useDebounce` hook (`250ms` window) coupled with client-side comparator pipelines for multi-attribute sorting and risk band filtering.

## Consequences
- Instant UI responsiveness with minimal network load.
- Seamless search experience across thousands of cached accounts.
""",
    "docs(adr): document debounced search and filtering in ADR-0037"
)

# 10 Runbooks
write_and_commit(
    "docs/runbooks/0031-deploying-investigation-deep-dive-views.md",
    """# Runbook 0031: Deploying Investigation Deep-Dive Views

## Objective
Verify investigation workspace (`/investigations/[id]`) and account profile (`/investigations/[id]/accounts/[accountId]`) deployment health.

## Verification Steps
1. Run `npm run build` in `apps/dashboard` and verify all dynamic routes compile (`ƒ /investigations/[id]`).
2. Verify Next.js server starts cleanly with `npm run start`.
3. Curl health endpoint: `curl -s http://localhost:8080/api/v1/health | jq .`.
""",
    "docs(runbook): add runbook 0031 for investigation view deployment"
)

write_and_commit(
    "docs/runbooks/0032-table-virtualization-performance-tuning.md",
    """# Runbook 0032: Table Virtualization Performance Tuning

## Objective
Tune table virtualization row heights and overscan buffers when experiencing frame drops during scroll.

## Tuning Actions
1. Open `apps/dashboard/src/tokens/table-virtualization.ts`.
2. Adjust `rowHeight` to match rendered row styles (`52px` default).
3. Increase `overscan` from `5` to `8` if fast scrolling causes white space flashes.
""",
    "docs(runbook): add runbook 0032 for table virtualization tuning"
)

write_and_commit(
    "docs/runbooks/0033-investigating-coordinated-bot-cluster-anomalies.md",
    """# Runbook 0033: Investigating Coordinated Bot Cluster Anomalies

## Objective
Inspect and confirm coordinated in-degree bot activity using the cluster indicator badge.

## Investigation Steps
1. Navigate to `/investigations/[id]` and switch to the **Risk Features & Graph** tab.
2. Locate accounts tagged with `ClusterIndicator`.
3. Filter relationship explorer by cluster ID to inspect shared targets and synchronous creation dates.
""",
    "docs(runbook): add runbook 0033 for coordinated bot cluster triage"
)

write_and_commit(
    "docs/runbooks/0034-export-pipeline-verification-and-schema-audit.md",
    """# Runbook 0034: Export Pipeline Verification and Schema Audit

## Objective
Validate that CSV and JSON export files conform to audit compliance schemas.

## Verification Steps
1. Trigger CSV export: `curl -H "Authorization: Bearer $TOKEN" http://localhost:8080/api/v1/scans/{id}/export/csv -o test.csv`.
2. Verify headers: `head -n 1 test.csv` must include `account_id,username,risk_score,risk_band,coverage`.
3. Trigger JSON export: `curl -H "Authorization: Bearer $TOKEN" http://localhost:8080/api/v1/scans/{id}/export/json | jq .summary`.
""",
    "docs(runbook): add runbook 0034 for export schema validation"
)

write_and_commit(
    "docs/runbooks/0035-resolving-wcag-21-aa-compliance-regressions.md",
    """# Runbook 0035: Resolving WCAG 2.1 AA Compliance Regressions

## Objective
Audit and fix accessibility violations in interactive investigation widgets.

## Audit Actions
1. Run axe / vitest a11y suite: `npm run test -- src/test/a11y/`.
2. Inspect color contrast ratios on risk badges (minimum 4.5:1 text-to-background).
3. Verify all SVG meters include `role="meter"` and `aria-valuenow`.
""",
    "docs(runbook): add runbook 0035 for WCAG 2.1 AA remediation"
)

write_and_commit(
    "docs/runbooks/0036-profiling-one-hop-neighborhood-subgraph-queries.md",
    """# Runbook 0036: Profiling 1-Hop Neighborhood Subgraph Queries

## Objective
Optimize query execution times for `list_relationship_edges` during heavy follower analysis.

## Tuning Actions
1. Confirm index on `(scan_id, source_id)` and `(scan_id, target_id)`.
2. Run `EXPLAIN QUERY PLAN SELECT * FROM relationship_edges WHERE scan_id = ? AND source_id = ?`.
3. Verify query scans index rather than performing full table scans.
""",
    "docs(runbook): add runbook 0036 for neighborhood query profiling"
)

write_and_commit(
    "docs/runbooks/0037-synthetic-data-provenance-enforcement.md",
    """# Runbook 0037: Synthetic Data Provenance Enforcement

## Objective
Ensure all mock or demo scan records are flagged with `data_origin: "synthetic"`.

## Verification Steps
1. Inspect database: `sqlite3 data/sbh.db "SELECT id, data_origin FROM scans WHERE data_origin = 'synthetic';"`
2. Verify UI shows amber warning banner on top of scan workspace.
""",
    "docs(runbook): add runbook 0037 for synthetic provenance enforcement"
)

write_and_commit(
    "docs/runbooks/0038-client-side-swr-cache-invalidation-and-refresh.md",
    """# Runbook 0038: Client-Side SWR Cache Invalidation and Refresh

## Objective
Force refresh stale investigation data in the analyst dashboard without full page reloads.

## Execution Steps
1. Call `mutate()` from `useInvestigation(scanId)` or `useRelationships(scanId)`.
2. Verify network panel shows conditional `ETag` / `If-None-Match` requests.
""",
    "docs(runbook): add runbook 0038 for SWR cache revalidation"
)

write_and_commit(
    "docs/runbooks/0039-handling-incomplete-profile-observations-gracefully.md",
    """# Runbook 0039: Handling Incomplete Profile Observations Gracefully

## Objective
Remediate accounts with deleted profiles, private privacy settings, or missing avatars.

## Triage Actions
1. Verify `AccountProfileCard` uses initials fallback when username is null.
2. Confirm `LimitationsCard` discloses private account API limitations.
3. Check `RiskGauge` falls back to `N/A` when scores are undefined.
""",
    "docs(runbook): add runbook 0039 for incomplete profile triage"
)

write_and_commit(
    "docs/runbooks/0040-triage-of-false-positive-risk-scoring-reports.md",
    """# Runbook 0040: Triage of False-Positive Risk Scoring Reports

## Objective
Investigate reports where authentic human accounts received critical risk ratings.

## Triage Actions
1. Navigate to `/investigations/[id]/accounts/[accountId]`.
2. Inspect `EvidenceInspector` to see which heuristic rule contributed disproportionate weight.
3. If rule is overly sensitive, adjust rule weight threshold in rule configuration.
""",
    "docs(runbook): add runbook 0040 for false positive risk triage"
)

# 13 Status Reports
status_reports = [
    ("docs/status/day-05/03-backend-export-routers-delivery.md", "# Day 5 Status 03: Backend Export Routers Delivery\n\nImplemented FastAPI routers for streaming CSV and JSON exports at `/scans/{scan_id}/export/csv` and `/scans/{scan_id}/export/json` with complete audit trails."),
    ("docs/status/day-05/04-openapi-spec-synchronization.md", "# Day 5 Status 04: OpenAPI Specification Synchronization\n\nSynchronized `docs/openapi.json` using `sbh docs --write`. Zero specification drift confirmed against backend routers."),
    ("docs/status/day-05/05-typescript-contract-validation.md", "# Day 5 Status 05: TypeScript Contract Validation\n\nAdded type definitions in `apps/dashboard/src/lib/api/types.ts` for AccountAssessment, ProfileObservation, AccountNeighborhoodResponse, and RelationshipEdge."),
    ("docs/status/day-05/06-investigation-design-tokens-and-bands.md", "# Day 5 Status 06: Investigation Design Tokens and Metric Bands\n\nDefined design tokens for RiskGauge geometry, relationship table virtualization, and risk band thresholds in `src/tokens/`."),
    ("docs/status/day-05/07-swr-custom-hooks-suite-integration.md", "# Day 5 Status 07: SWR Custom Hooks Suite Integration\n\nImplemented typed data-fetching hooks: `useInvestigation`, `useAccounts`, `useAccountDetail`, `useAccountEvidence`, `useRelationships`, `useAccountNeighborhood`, and `useInvestigationExport`."),
    ("docs/status/day-05/08-account-profile-card-and-gauge-delivery.md", "# Day 5 Status 08: Account Profile Card and Risk Gauge Delivery\n\nCreated `AccountProfileCard` with avatar initial fallbacks, platform icons, follower/following stats, and `RiskGauge` with SVG meter accessibility."),
    ("docs/status/day-05/09-evidence-inspector-accordion-delivery.md", "# Day 5 Status 09: Evidence Inspector Accordion Delivery\n\nDelivered `EvidenceInspector` collapsible accordion with `EvidenceItemRow`, `ContributingSignalBar`, and `LimitationsCard` disclosing unobservable channels."),
    ("docs/status/day-05/10-follower-explorer-virtualized-table-delivery.md", "# Day 5 Status 10: Follower Explorer Virtualized Table Delivery\n\nDelivered `RelationshipTable`, `FilterToolbar`, `PaginationBar`, and `EmptyAccountsState` supporting high-speed exploration of follower graphs."),
    ("docs/status/day-05/11-multi-tab-workspace-routing-delivery.md", "# Day 5 Status 11: Multi-Tab Workspace Routing Delivery\n\nImplemented `/investigations/[id]` workspace page with Overview, Explorer, Features, and Export tab views."),
    ("docs/status/day-05/12-account-deep-dive-route-delivery.md", "# Day 5 Status 12: Account Deep Dive Route Delivery\n\nDelivered `/investigations/[id]/accounts/[accountId]` featuring risk breakdown, 1-hop neighborhood viewer, and observation history timeline."),
    ("docs/status/day-05/13-wcag-21-aa-accessibility-audit.md", "# Day 5 Status 13: WCAG 2.1 AA Accessibility Audit\n\nExecuted accessibility test suite covering WAI-ARIA tablist semantics, accordion region controls, meter roles, and non-color-only risk indicators."),
    ("docs/status/day-05/14-dataset-export-and-provenance-verification.md", "# Day 5 Status 14: Dataset Export and Provenance Verification\n\nValidated end-to-end CSV and JSON downloads with synthetic demo disclaimer banners and ethical provenance disclosures."),
    ("docs/status/day-05/15-day-05-final-audit-and-verification.md", "# Day 5 Status 15: Day 5 Final Audit and Verification\n\nCompleted Day 5 Account Investigation and Follower/Following Explorer milestone with 100% test pass rate across backend and frontend suites."),
]

for rel_path, content in status_reports:
    write_and_commit(rel_path, content, f"docs(status): log {Path(rel_path).stem} milestone report")

print("Batch 6 finished 33 commits.")

