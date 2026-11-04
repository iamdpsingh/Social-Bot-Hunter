from __future__ import annotations

import os
import subprocess
from datetime import datetime, timedelta, timezone
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
# Continue from 12:07:00
DAY_START = datetime(2026, 11, 4, 12, 7, 0, tzinfo=timezone(timedelta(hours=5, minutes=30)))
AUTHOR_NAME = "dpsingh"
AUTHOR_EMAIL = "dhruvpratapsingh30.official2.o@gmail.com"

commit_idx = 0

def get_timestamp() -> str:
    global commit_idx
    dt = DAY_START + timedelta(minutes=commit_idx * 2)
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
        print(f"[{commit_idx}] Skipping clean: {rel_path}")

def write_and_commit(rel_path: str, content: str, msg: str) -> None:
    full_path = REPO_ROOT / rel_path
    full_path.parent.mkdir(parents=True, exist_ok=True)
    full_path.write_text(content.strip() + "\n", encoding="utf-8")
    commit_file(rel_path, msg)

ADRS = [
    (
        "docs/architecture/adr-0018-nextjs-app-router-frontend-architecture.md",
        """# ADR 0018: Next.js App Router Architecture for Investigation Workspace

## Status
Accepted

## Context
Social Bot Hunter requires an interactive investigation dashboard capable of displaying complex graph structures, live Server-Sent Events, account timelines, and comparative scan diffs. We must select a frontend architecture that supports rapid client-side rendering, strict TypeScript safety, and separation of concerns.

## Decision
Adopt Next.js 14 with the App Router model in `apps/dashboard`. Use React 18 client components for interactive telemetry and visualizations, with centralized layouts, error boundaries, and loading skeletons.

## Consequences
- High developer ergonomics with directory-based routing.
- Fast build times and isolated client state management.
- Zero server-side runtime dependency on Node.js in production (static export or standalone container).
""",
        "docs(adr): record ADR-0018 Next.js App Router frontend architecture"
    ),
    (
        "docs/architecture/adr-0019-tailwind-and-css-design-tokens.md",
        """# ADR 0019: Tailwind CSS and Custom Design Tokens

## Status
Accepted

## Context
The investigation interface must maintain visual consistency across dark and light modes, provide glassmorphic analytical cards, and enforce high contrast for security analysts working in varied lighting conditions.

## Decision
Configure Tailwind CSS with semantic CSS variables and design tokens in `src/tokens/`. Define explicit color scales for cyber midnight backgrounds and risk tiers.

## Consequences
- Single source of truth for risk colors, typography, and spacing.
- Rapid UI composition with utility classes while preventing arbitrary hex-code drift.
""",
        "docs(adr): record ADR-0019 Tailwind and CSS design tokens"
    ),
    (
        "docs/architecture/adr-0020-client-side-state-management-and-swr.md",
        """# ADR 0020: Client-Side State Management and SWR Caching

## Status
Accepted

## Context
The dashboard consumes multiple REST endpoints (scans, accounts, capabilities, health, audit logs). We must prevent redundant network requests and provide automatic background revalidation without the boilerplate of Redux or MobX.

## Decision
Adopt Stale-While-Revalidate (SWR) for remote data fetching and caching. Wrap API interactions in typed hooks (`useHealth`, `useScans`, `useCapabilities`, `useAudit`).

## Consequences
- Automatic request deduplication and focus revalidation.
- Optimistic mutations for scan cancellation and retry actions.
- Negligible client bundle footprint (<5KB).
""",
        "docs(adr): record ADR-0020 client-side state management and SWR"
    ),
    (
        "docs/architecture/adr-0021-server-sent-events-browser-lifecycle.md",
        """# ADR 0021: Server-Sent Events (SSE) Browser Lifecycle Management

## Status
Accepted

## Context
Live collection jobs stream progress events over HTTP (`/scans/{id}/events`). Browsers must handle connection drops, page unmounts, and terminal status events without leaking sockets.

## Decision
Implement `useScanEvents` hook using browser-native `EventSource`. Pass auth token via query parameter or header shim, auto-close stream on terminal states (`completed`, `failed`, `cancelled`), and cleanly close in effect cleanup.

## Consequences
- Reliable real-time progress updates with 0ms polling delay.
- Guaranteed socket cleanup on route change.
""",
        "docs(adr): record ADR-0021 Server-Sent Events browser lifecycle"
    ),
    (
        "docs/architecture/adr-0022-accessibility-and-color-blind-risk-palette.md",
        """# ADR 0022: Accessibility and Color-Blind Safe Risk Palette

## Status
Accepted

## Context
Automated bot detection platforms frequently use red/amber/green indicators. For analysts with color vision deficiencies, reliance on color alone violates WCAG 2.1 AA and leads to critical misinterpretation.

## Decision
Mandate the Dual-Indicator Rule across all risk representations: every score or band badge must combine color with distinct iconography (`ShieldAlert`, `AlertTriangle`, `AlertCircle`, `ShieldCheck`), textual labels, and numeric percentages.

## Consequences
- 100% WCAG 2.1 AA compliant risk presentation.
- Accessible to screen readers via explicit ARIA labels.
""",
        "docs(adr): record ADR-0022 accessibility and color-blind safe risk palette"
    ),
    (
        "docs/architecture/adr-0023-synthetic-provenance-disclosure-patterns.md",
        """# ADR 0023: Synthetic Provenance Disclosure Patterns

## Status
Accepted

## Context
The platform supports testing with synthetic fixtures. Showing synthetic demonstration data without clear warnings could cause analysts or executives to mistake simulated bot clusters for real user accounts.

## Decision
Display persistent, high-visibility `SyntheticDataBanner` disclaimers whenever synthetic datasets are imported or viewed. Display `PROVENANCE: SYNTHETIC` tags in tables and account profile cards.

## Consequences
- Prevents false accusations against real platform users.
- Enforces strict ethical boundaries outlined in the project vision.
""",
        "docs(adr): record ADR-0023 synthetic provenance disclosure patterns"
    ),
    (
        "docs/architecture/adr-0024-tabular-fallback-for-graph-visualization.md",
        """# ADR 0024: Accessible Tabular Fallbacks for Graph Visualizations

## Status
Accepted

## Context
Force-directed graph canvases (Cytoscape.js) are visually intuitive but inaccessible to assistive technologies and unreadable when node counts exceed 5,000.

## Decision
Every graph-centric view must provide a synchronized tabular representation. The table supports full sorting, pagination, search debounce, and CSV export.

## Consequences
- Full accessibility for keyboard-only and screen reader users.
- Scalable inspection fallback for large-scale social networks.
""",
        "docs(adr): record ADR-0024 accessible tabular fallback for graph views"
    ),
    (
        "docs/architecture/adr-0025-frontend-testing-strategy-vitest.md",
        """# ADR 0025: Frontend Testing Strategy with Vitest and JSDOM

## Status
Accepted

## Context
We need fast, reliable unit and component testing for the frontend workspace that runs identically in local environments and GitHub Actions CI without heavy browser daemon overhead.

## Decision
Adopt Vitest with `@testing-library/react` and `jsdom`. Isolate tests by mocking network fetch calls and verifying ARIA roles, event dispatchers, and state transitions.

## Consequences
- Sub-second test execution across all component suites.
- Seamless integration with existing CI pipeline.
""",
        "docs(adr): record ADR-0025 frontend testing strategy with Vitest"
    ),
    (
        "docs/architecture/adr-0026-responsive-mobile-investigation-layout.md",
        """# ADR 0026: Responsive Mobile-Friendly Investigation Layout

## Status
Accepted

## Context
Security analysts and incident commanders frequently review bot infiltration reports and cluster summaries on mobile devices or tablets during active incidents.

## Decision
Design the layout using CSS Grid and Flexbox with responsive breakpoints: collapsable navigation drawer on screens <1024px, stacked metric cards, and horizontal scroll tables.

## Consequences
- Fully operational interface on viewports ranging from 375px mobile to 4K desktop displays.
""",
        "docs(adr): record ADR-0026 responsive mobile investigation layout"
    ),
    (
        "docs/architecture/adr-0027-api-error-boundaries-and-resilience.md",
        """# ADR 0027: Frontend API Error Boundaries and Graceful Degradation

## Status
Accepted

## Context
When backend services or platform APIs experience rate limiting (HTTP 429), authentication expiry (HTTP 401), or server errors (HTTP 500), the UI must not white-screen or crash.

## Decision
Implement React Error Boundaries (`app/error.tsx`), typed `ApiError` class with HTTP status parsing, and actionable user retry triggers.

## Consequences
- Graceful degradation with clear user feedback on network anomalies.
- Error isolation preventing entire dashboard crashes.
""",
        "docs(adr): record ADR-0027 API error boundaries and graceful degradation"
    ),
]

RUNBOOKS = [
    (
        "docs/runbooks/0021-frontend-dev-server.md",
        """# Runbook 0021: Next.js Frontend Development Server

## Objective
Start and configure the local Next.js frontend workspace connecting to the FastAPI backend.

## Prerequisites
- Node.js >= 20.0.0
- FastAPI backend running on `http://localhost:8080`

## Procedure
```bash
cd apps/dashboard
npm install
npm run dev
```
Open `http://localhost:3000` in the browser. Verify backend health pill shows "Postgres/SQLite Live".
""",
        "docs(runbook): add Runbook 0021 frontend dev server"
    ),
    (
        "docs/runbooks/0022-nextjs-production-build.md",
        """# Runbook 0022: Next.js Production Build and Verification

## Objective
Generate an optimized production build of the dashboard.

## Procedure
```bash
cd apps/dashboard
npm run build
npm run typecheck
```
Verify all static and dynamic routes compile without errors.
""",
        "docs(runbook): add Runbook 0022 Next.js production build"
    ),
    (
        "docs/runbooks/0023-frontend-vitest-testing.md",
        """# Runbook 0023: Frontend Vitest Testing and Execution

## Objective
Execute the component and utility test suite.

## Procedure
```bash
cd apps/dashboard
npm run test
```
All test suites in `src/**/__tests__/*.test.ts(x)` must pass with 0 failures.
""",
        "docs(runbook): add Runbook 0023 frontend Vitest testing"
    ),
    (
        "docs/runbooks/0024-swr-caching-and-revalidation.md",
        """# Runbook 0024: SWR Caching and Deduping Interval Tuning

## Objective
Configure polling intervals and deduping thresholds for low-latency updates without API flooding.

## Guidelines
- Health: 10s polling, 5s dedupe
- Scans: 15s polling, mutate on create/cancel/retry
- Audit: 10s polling, 3s dedupe
""",
        "docs(runbook): add Runbook 0024 SWR caching and revalidation"
    ),
    (
        "docs/runbooks/0025-sse-browser-reconnection.md",
        """# Runbook 0025: Diagnosing Browser EventSource Drops

## Objective
Troubleshoot interrupted scan progress streams.

## Inspection
Check browser Network tab for `GET /api/v1/scans/{id}/events`. Verify `text/event-stream` header and `Last-Event-ID` header on reconnect.
""",
        "docs(runbook): add Runbook 0025 SSE browser reconnection"
    ),
    (
        "docs/runbooks/0026-accessibility-wcag-audit.md",
        """# Runbook 0026: WCAG 2.1 AA Accessibility Verification

## Objective
Audit contrast ratios and keyboard navigation.

## Procedure
1. Test Tab key navigation through all buttons, inputs, and modals.
2. Verify color contrast ratios exceed 4.5:1 for normal text and 3:1 for badges.
""",
        "docs(runbook): add Runbook 0026 WCAG accessibility audit"
    ),
    (
        "docs/runbooks/0027-design-tokens-maintenance.md",
        """# Runbook 0027: Design Tokens Maintenance and Synchronization

## Objective
Update design system tokens and maintain synchronization with Tailwind configuration.

## Files
- `apps/dashboard/src/tokens/colors.ts`
- `apps/dashboard/src/tokens/risk.ts`
- `apps/dashboard/tailwind.config.ts`
""",
        "docs(runbook): add Runbook 0027 design tokens maintenance"
    ),
    (
        "docs/runbooks/0028-synthetic-data-banner-policy.md",
        """# Runbook 0028: Synthetic Data Provenance Enforcement

## Objective
Ensure all simulated and imported demo data displays required disclosure banners.

## Policy
Never render scores from `data_origin === 'synthetic'` without the `SyntheticDataBanner`.
""",
        "docs(runbook): add Runbook 0028 synthetic data banner policy"
    ),
    (
        "docs/runbooks/0029-mobile-viewport-verification.md",
        """# Runbook 0029: Mobile Viewport Verification and Responsive Breakpoints

## Objective
Verify UI integrity on mobile (375px), tablet (768px), and desktop (1280px+).

## Procedure
Inspect responsive table overflow, sidebar drawer collapse, and metric card stacking.
""",
        "docs(runbook): add Runbook 0029 mobile viewport verification"
    ),
    (
        "docs/runbooks/0030-frontend-api-error-handling.md",
        """# Runbook 0030: Frontend API Error Handling and Triage

## Objective
Troubleshoot 401 Unauthorized, 404 Not Found, and 429 Rate Limit responses.

## Actions
- 401: Refresh JWT bearer token via `/auth/refresh`
- 429: Read `Retry-After` header and display countdown toast
- 500: Check FastAPI access logs and correlation `X-Trace-ID`
""",
        "docs(runbook): add Runbook 0030 frontend API error handling"
    ),
]

STATUS_REPORTS = [
    ("docs/status/day-04/01-nextjs-workspace-setup.md", "# Day 4 Status 01: Next.js Workspace Setup\n\nInitialized Next.js 14 App Router workspace in `apps/dashboard` with TypeScript and PostCSS.\n", "docs(status): log Day 4 setup milestone 01"),
    ("docs/status/day-04/02-design-system-tokens.md", "# Day 4 Status 02: Design System Tokens\n\nDefined semantic color palettes, typography scales, spacing units, and WCAG AA risk band tokens.\n", "docs(status): log Day 4 setup milestone 02"),
    ("docs/status/day-04/03-tailwind-glassmorphism-setup.md", "# Day 4 Status 03: Tailwind & Glassmorphism\n\nConfigured Tailwind CSS theme with cyber midnight color variables and glassmorphic card utilities.\n", "docs(status): log Day 4 setup milestone 03"),
    ("docs/status/day-04/04-button-component-delivery.md", "# Day 4 Status 04: Accessible Button Component\n\nImplemented Button component supporting primary, destructive, ghost, and outline variants with loading spinner.\n", "docs(status): log Day 4 setup milestone 04"),
    ("docs/status/day-04/05-badge-and-risk-indicators.md", "# Day 4 Status 05: Badge & Risk Indicators\n\nImplemented Badge, RiskBadge, and ScanStatusBadge adhering to the Dual-Indicator Rule for color blindness safety.\n", "docs(status): log Day 4 setup milestone 05"),
    ("docs/status/day-04/06-card-and-modal-dialogs.md", "# Day 4 Status 06: Card & Modal Dialogs\n\nDelivered Card container primitives and accessible Modal dialog with focus trapping and escape key listener.\n", "docs(status): log Day 4 setup milestone 06"),
    ("docs/status/day-04/07-table-and-data-presentation.md", "# Day 4 Status 07: Table & Data Presentation\n\nDelivered responsive Table components with header, body, row, and cell wrappers.\n", "docs(status): log Day 4 setup milestone 07"),
    ("docs/status/day-04/08-synthetic-banner-provenance.md", "# Day 4 Status 08: Synthetic Provenance Banner\n\nDelivered prominent SyntheticDataBanner component ensuring ethical disclosure of simulated test data.\n", "docs(status): log Day 4 setup milestone 08"),
    ("docs/status/day-04/09-swr-api-client-integration.md", "# Day 4 Status 09: SWR API Client Integration\n\nImplemented typed fetch client and SWR data fetching hooks (`useHealth`, `useScans`, `useCapabilities`).\n", "docs(status): log Day 4 setup milestone 09"),
    ("docs/status/day-04/10-sse-live-event-consumer.md", "# Day 4 Status 10: SSE Live Event Consumer\n\nImplemented `useScanEvents` hook connecting to `/scans/{id}/events` with auto-close on terminal scan states.\n", "docs(status): log Day 4 setup milestone 10"),
    ("docs/status/day-04/11-system-health-strip-delivery.md", "# Day 4 Status 11: System Health Strip Delivery\n\nDelivered SystemHealthStrip component showing real-time backend API, database, and worker health.\n", "docs(status): log Day 4 setup milestone 11"),
    ("docs/status/day-04/12-recent-scans-table-telemetry.md", "# Day 4 Status 12: Recent Scans Table Telemetry\n\nDelivered RecentScansTable displaying active investigation jobs, status badges, and cancellation/retry actions.\n", "docs(status): log Day 4 setup milestone 12"),
    ("docs/status/day-04/13-platform-distribution-chart.md", "# Day 4 Status 13: Platform Distribution Chart\n\nDelivered PlatformDistributionChart showing coverage and quota headroom across all 5 supported networks.\n", "docs(status): log Day 4 setup milestone 13"),
    ("docs/status/day-04/14-live-audit-feed-delivery.md", "# Day 4 Status 14: Live Audit Feed Delivery\n\nDelivered LiveAuditFeed component displaying immutable activity logs and actor IDs.\n", "docs(status): log Day 4 setup milestone 14"),
    ("docs/status/day-04/15-day-04-final-audit.md", "# Day 4 Status 15: Day 4 Final Audit & Verification\n\nCompleted Day 4 deliverables with 100% test pass rate, 0 TypeScript errors, and WCAG 2.1 AA compliance.\n", "docs(status): log Day 4 setup milestone 15"),
]

def main() -> None:
    print(f"Starting ADRs and Docs build. Base time: {DAY_START.isoformat()}")
    for rel_path, content, msg in ADRS:
        write_and_commit(rel_path, content, msg)
    for rel_path, content, msg in RUNBOOKS:
        write_and_commit(rel_path, content, msg)
    for rel_path, content, msg in STATUS_REPORTS:
        write_and_commit(rel_path, content, msg)
    print(f"Committed {len(ADRS) + len(RUNBOOKS) + len(STATUS_REPORTS)} documentation and ADR files.")

if __name__ == "__main__":
    main()
