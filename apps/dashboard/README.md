# Social Bot Hunter — Analytics & Investigation Dashboard

Frontend workspace for Social Bot Hunter. Built with Next.js (App Router), TypeScript, and Cytoscape.js for interactive network visualization.

## Views

1. **Overview (`/`)**: Recent investigations, scan status, summary cards, pipeline health, data coverage.
2. **Account Investigation (`/investigations/[scan_id]/accounts/[account_id]`)**: Profile observations, risk assessment breakdown, feature availability, and evidence records.
3. **Follower & Following Explorer (`/investigations/[scan_id]/relationships`)**: Search, filter by risk band, pagination, relationship direction (distinguishing observed subset from total).
4. **Network Explorer (`/investigations/[scan_id]/network`)**: Interactive Cytoscape.js directed graph, cluster filtering, node inspection panel, accessible table view.
5. **Coordinated Activity (`/investigations/[scan_id]/coordination`)**: Repeated content templates, shared target analysis, synchrony signals, alternative explanations.
6. **Scan History & Diff (`/history`)**: Compare historical scans (`/diff`), identify confirmed additions/removals vs coverage gaps.
7. **Data Sources & Settings (`/settings`)**: Platform capability registry, quota status, audit logs, retention sweep triggers.

## Architecture & Design Guidelines

- **Evidence First**: Every risk score displays its contributing features, data coverage %, and limitations.
- **Clear Synthetic Banners**: Demo datasets are clearly flagged with warning banners (`SYNTHETIC DEMO DATA`).
- **Accessible & Color-Blind Friendly**: Color is never the sole indicator for risk bands (uses distinct iconography, tags, and numeric values).
- **Tabular Fallbacks**: Every graph view provides a full table representation for accessibility and large datasets.

## Development

```bash
# Target setup:
cd apps/dashboard
npm install
npm run dev
```
Connects to the FastAPI backend running at `http://localhost:8080/api/v1` (configured via `NEXT_PUBLIC_API_URL`).
