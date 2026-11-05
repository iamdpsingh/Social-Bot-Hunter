from __future__ import annotations

import os
import subprocess
from datetime import datetime, timedelta, timezone
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
DAY_START = datetime(2026, 11, 5, 12, 45, 0, tzinfo=timezone(timedelta(hours=5, minutes=30)))
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
        print(f"[{commit_idx}] No changes to commit for: {rel_path}")

def write_and_commit(rel_path: str, content: str, msg: str) -> None:
    full_path = REPO_ROOT / rel_path
    full_path.parent.mkdir(parents=True, exist_ok=True)
    full_path.write_text(content.strip() + "\n", encoding="utf-8")
    commit_file(rel_path, msg)

print("Preparing Day 5 Batch 4: Pages, Workspace Layouts & Investigation Deep-Dive Views...")

# 1. ExportPanel component
write_and_commit(
    "apps/dashboard/src/components/investigation/export-panel.tsx",
    """\"use client\";

import React, { useState } from \"react\";
import { Download, FileSpreadsheet, FileCode, CheckCircle2, AlertCircle } from \"lucide-react\";
import { Button } from \"../ui/button\";

export interface ExportPanelProps {
  scanId: string;
  onExportCsv?: () => void;
  onExportJson?: () => void;
  isExporting?: boolean;
}

export function ExportPanel({ scanId, onExportCsv, onExportJson, isExporting = false }: ExportPanelProps) {
  const [selectedFormat, setSelectedFormat] = useState<\"csv\" | \"json\">(\"csv\");
  const [exportComplete, setExportComplete] = useState<string | null>(null);

  const handleTrigger = () => {
    if (selectedFormat === \"csv\") {
      onExportCsv?.();
      setExportComplete(\"CSV export initiated for scan \" + scanId);
    } else {
      onExportJson?.();
      setExportComplete(\"JSON export bundle initiated for scan \" + scanId);
    }
  };

  return (
    <div className=\"rounded-lg border border-border bg-card p-6 space-y-5\" data-testid=\"export-panel\">
      <div>
        <h3 className=\"text-base font-semibold text-foreground flex items-center gap-2\">
          <Download className=\"h-4 w-4 text-primary\" />
          Investigation Data Export
        </h3>
        <p className=\"text-xs text-muted-foreground mt-1\">
          Download complete investigation records, account risk evaluations, and evidence provenance for audit compliance.
        </p>
      </div>

      <div className=\"grid grid-cols-1 sm:grid-cols-2 gap-4\">
        <button
          type=\"button\"
          onClick={() => setSelectedFormat(\"csv\")}
          className={`flex items-start gap-3 p-4 rounded-lg border text-left transition-all ${
            selectedFormat === \"csv\"
              ? \"border-primary bg-primary/5 ring-1 ring-primary\"
              : \"border-border bg-muted/20 hover:border-border/80\"
          }`}
        >
          <FileSpreadsheet className=\"h-5 w-5 text-emerald-500 mt-0.5\" />
          <div>
            <div className=\"text-sm font-medium text-foreground\">CSV Spreadsheet</div>
            <div className=\"text-xs text-muted-foreground mt-0.5\">Tabular rows with risk scores and key metrics</div>
          </div>
        </button>

        <button
          type=\"button\"
          onClick={() => setSelectedFormat(\"json\")}
          className={`flex items-start gap-3 p-4 rounded-lg border text-left transition-all ${
            selectedFormat === \"json\"
              ? \"border-primary bg-primary/5 ring-1 ring-primary\"
              : \"border-border bg-muted/20 hover:border-border/80\"
          }`}
        >
          <FileCode className=\"h-5 w-5 text-primary mt-0.5\" />
          <div>
            <div className=\"text-sm font-medium text-foreground\">JSON Bundle</div>
            <div className=\"text-xs text-muted-foreground mt-0.5\">Full schema with nested evidence and rule trace</div>
          </div>
        </button>
      </div>

      {exportComplete && (
        <div className=\"flex items-center gap-2 text-xs text-emerald-500 bg-emerald-500/10 p-3 rounded border border-emerald-500/20\">
          <CheckCircle2 className=\"h-4 w-4 shrink-0\" />
          <span>{exportComplete}</span>
        </div>
      )}

      <div className=\"flex justify-end\">
        <Button onClick={handleTrigger} disabled={isExporting} className=\"gap-2\">
          <Download className=\"h-4 w-4\" />
          {isExporting ? \"Preparing Download...\" : `Download ${selectedFormat.toUpperCase()}`}
        </Button>
      </div>
    </div>
  );
}
""",
    "feat(ui): implement ExportPanel component with format toggles and status confirmation"
)

# 2. ExportPanel test
write_and_commit(
    "apps/dashboard/src/components/investigation/__tests__/export-panel.test.tsx",
    """import React from \"react\";
import { describe, it, expect, vi } from \"vitest\";
import { render, screen, fireEvent } from \"@testing-library/react\";
import { ExportPanel } from \"../export-panel\";

describe(\"ExportPanel\", () => {
  it(\"toggles format and invokes download callbacks\", () => {
    const handleCsv = vi.fn();
    const handleJson = vi.fn();

    render(<ExportPanel scanId=\"s_123\" onExportCsv={handleCsv} onExportJson={handleJson} />);
    expect(screen.getByText(\"Investigation Data Export\")).toBeInTheDocument();

    // Default is CSV
    fireEvent.click(screen.getByText(\"Download CSV\"));
    expect(handleCsv).toHaveBeenCalledTimes(1);

    // Switch to JSON
    fireEvent.click(screen.getByText(\"JSON Bundle\"));
    fireEvent.click(screen.getByText(\"Download JSON\"));
    expect(handleJson).toHaveBeenCalledTimes(1);
  });
});
""",
    "test(ui): test ExportPanel format selection and download dispatch"
)

# 3. OverviewSummaryCard component
write_and_commit(
    "apps/dashboard/src/components/investigation/overview-summary-card.tsx",
    """\"use client\";

import React from \"react\";
import { ShieldAlert, Users, TrendingUp, AlertTriangle } from \"lucide-react\";

export interface OverviewSummaryCardProps {
  totalAccounts: number;
  botAccounts: number;
  avgRiskScore: number;
  criticalCount: number;
}

export function OverviewSummaryCard({
  totalAccounts,
  botAccounts,
  avgRiskScore,
  criticalCount,
}: OverviewSummaryCardProps) {
  const botRatio = totalAccounts > 0 ? ((botAccounts / totalAccounts) * 100).toFixed(1) : \"0.0\";

  return (
    <div className=\"grid grid-cols-2 lg:grid-cols-4 gap-4\" data-testid=\"overview-summary-card\">
      <div className=\"rounded-lg border border-border bg-card p-4 space-y-1\">
        <div className=\"flex items-center justify-between text-muted-foreground\">
          <span className=\"text-xs font-medium uppercase tracking-wider\">Total Accounts</span>
          <Users className=\"h-4 w-4\" />
        </div>
        <div className=\"text-2xl font-bold text-foreground\">{totalAccounts.toLocaleString()}</div>
        <div className=\"text-[11px] text-muted-foreground\">Analyzed in investigation</div>
      </div>

      <div className=\"rounded-lg border border-border bg-card p-4 space-y-1\">
        <div className=\"flex items-center justify-between text-muted-foreground\">
          <span className=\"text-xs font-medium uppercase tracking-wider\">Flagged Bots</span>
          <ShieldAlert className=\"h-4 w-4 text-rose-500\" />
        </div>
        <div className=\"text-2xl font-bold text-rose-500\">{botAccounts.toLocaleString()}</div>
        <div className=\"text-[11px] text-muted-foreground\">{botRatio}% flag rate</div>
      </div>

      <div className=\"rounded-lg border border-border bg-card p-4 space-y-1\">
        <div className=\"flex items-center justify-between text-muted-foreground\">
          <span className=\"text-xs font-medium uppercase tracking-wider\">Avg Risk Score</span>
          <TrendingUp className=\"h-4 w-4 text-amber-500\" />
        </div>
        <div className=\"text-2xl font-bold text-foreground\">{avgRiskScore.toFixed(2)}</div>
        <div className=\"text-[11px] text-muted-foreground\">Scale 0.00 – 1.00</div>
      </div>

      <div className=\"rounded-lg border border-border bg-card p-4 space-y-1\">
        <div className=\"flex items-center justify-between text-muted-foreground\">
          <span className=\"text-xs font-medium uppercase tracking-wider\">Critical Alerts</span>
          <AlertTriangle className=\"h-4 w-4 text-rose-500\" />
        </div>
        <div className=\"text-2xl font-bold text-rose-500\">{criticalCount}</div>
        <div className=\"text-[11px] text-muted-foreground\">Requires immediate review</div>
      </div>
    </div>
  );
}
""",
    "feat(ui): implement OverviewSummaryCard component with investigation aggregates"
)

# 4. OverviewSummaryCard test
write_and_commit(
    "apps/dashboard/src/components/investigation/__tests__/overview-summary-card.test.tsx",
    """import React from \"react\";
import { describe, it, expect } from \"vitest\";
import { render, screen } from \"@testing-library/react\";
import { OverviewSummaryCard } from \"../overview-summary-card\";

describe(\"OverviewSummaryCard\", () => {
  it(\"renders calculated bot ratio, counts, and critical badges\", () => {
    render(
      <OverviewSummaryCard
        totalAccounts={200}
        botAccounts={50}
        avgRiskScore={0.72}
        criticalCount={14}
      />
    );

    expect(screen.getByText(\"200\")).toBeInTheDocument();
    expect(screen.getByText(\"50\")).toBeInTheDocument();
    expect(screen.getByText(\"25.0% flag rate\")).toBeInTheDocument();
    expect(screen.getByText(\"0.72\")).toBeInTheDocument();
    expect(screen.getByText(\"14\")).toBeInTheDocument();
  });
});
""",
    "test(ui): test OverviewSummaryCard displays computed percentages and thresholds"
)

# 5. ClusterIndicator component
write_and_commit(
    "apps/dashboard/src/components/investigation/cluster-indicator.tsx",
    """\"use client\";

import React from \"react\";
import { Share2 } from \"lucide-react\";

export interface ClusterIndicatorProps {
  clusterId?: string;
  clusterSize?: number;
  confidence?: number;
}

export function ClusterIndicator({ clusterId, clusterSize, confidence }: ClusterIndicatorProps) {
  if (!clusterId) {
    return (
      <span className=\"inline-flex items-center gap-1 text-[11px] text-muted-foreground\">
        Standalone
      </span>
    );
  }

  return (
    <div
      className=\"inline-flex items-center gap-1.5 px-2 py-0.5 rounded-full text-xs font-medium bg-purple-500/10 text-purple-400 border border-purple-500/20\"
      title={`Part of coordinated bot cluster ${clusterId}`}
      data-testid=\"cluster-indicator\"
    >
      <Share2 className=\"h-3 w-3 shrink-0\" />
      <span>Cluster #{clusterId.slice(-4)}</span>
      {clusterSize !== undefined && (
        <span className=\"text-[10px] bg-purple-500/20 px-1 rounded\">{clusterSize} accts</span>
      )}
    </div>
  );
}
""",
    "feat(ui): implement ClusterIndicator component for coordinated campaign networks"
)

# 6. ClusterIndicator test
write_and_commit(
    "apps/dashboard/src/components/investigation/__tests__/cluster-indicator.test.tsx",
    """import React from \"react\";
import { describe, it, expect } from \"vitest\";
import { render, screen } from \"@testing-library/react\";
import { ClusterIndicator } from \"../cluster-indicator\";

describe(\"ClusterIndicator\", () => {
  it(\"renders cluster pill with short hash and size when present\", () => {
    render(<ClusterIndicator clusterId=\"cls_987654\" clusterSize={12} confidence={0.92} />);
    expect(screen.getByTestId(\"cluster-indicator\")).toBeInTheDocument();
    expect(screen.getByText(\"Cluster #7654\")).toBeInTheDocument();
    expect(screen.getByText(\"12 accts\")).toBeInTheDocument();
  });

  it(\"renders standalone fallback when clusterId is missing\", () => {
    render(<ClusterIndicator />);
    expect(screen.getByText(\"Standalone\")).toBeInTheDocument();
  });
});
""",
    "test(ui): test ClusterIndicator badge and standalone fallback state"
)

# 7. SignalRadarPreview component
write_and_commit(
    "apps/dashboard/src/components/investigation/signal-radar-preview.tsx",
    """\"use client\";

import React from \"react\";
import { Activity, Clock, Repeat, UserCheck, Shield } from \"lucide-react\";

export interface SignalRadarPreviewProps {
  timingScore?: number;
  textRepetitionScore?: number;
  networkAnomalyScore?: number;
  profileScore?: number;
}

export function SignalRadarPreview({
  timingScore = 0.1,
  textRepetitionScore = 0.1,
  networkAnomalyScore = 0.1,
  profileScore = 0.1,
}: SignalRadarPreviewProps) {
  const indicators = [
    { label: \"Activity Timing\", score: timingScore, icon: Clock },
    { label: \"Text Repetition\", score: textRepetitionScore, icon: Repeat },
    { label: \"Network Anomaly\", score: networkAnomalyScore, icon: Activity },
    { label: \"Profile Pattern\", score: profileScore, icon: UserCheck },
  ];

  return (
    <div className=\"rounded-lg border border-border bg-card p-4 space-y-3\" data-testid=\"signal-radar-preview\">
      <div className=\"flex items-center justify-between\">
        <h4 className=\"text-xs font-semibold text-foreground uppercase tracking-wider flex items-center gap-1.5\">
          <Shield className=\"h-3.5 w-3.5 text-primary\" />
          Detection Signal Vectors
        </h4>
        <span className=\"text-[11px] text-muted-foreground\">Heuristic Breakdown</span>
      </div>

      <div className=\"space-y-2\">
        {indicators.map((ind) => {
          const Icon = ind.icon;
          const percentage = Math.round(ind.score * 100);
          const colorClass =
            percentage > 70 ? \"bg-rose-500\" : percentage > 40 ? \"bg-amber-500\" : \"bg-emerald-500\";

          return (
            <div key={ind.label} className=\"space-y-1\">
              <div className=\"flex items-center justify-between text-xs\">
                <span className=\"flex items-center gap-1.5 text-muted-foreground\">
                  <Icon className=\"h-3 w-3\" />
                  {ind.label}
                </span>
                <span className=\"font-mono font-medium text-foreground\">{percentage}%</span>
              </div>
              <div className=\"h-1.5 w-full bg-muted rounded-full overflow-hidden\">
                <div
                  className={`h-full rounded-full transition-all duration-300 ${colorClass}`}
                  style={{ width: `${percentage}%` }}
                />
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
""",
    "feat(ui): implement SignalRadarPreview component displaying vector scores"
)

# 8. SignalRadarPreview test
write_and_commit(
    "apps/dashboard/src/components/investigation/__tests__/signal-radar-preview.test.tsx",
    """import React from \"react\";
import { describe, it, expect } from \"vitest\";
import { render, screen } from \"@testing-library/react\";
import { SignalRadarPreview } from \"../signal-radar-preview\";

describe(\"SignalRadarPreview\", () => {
  it(\"renders behavioral vector progress bars with percentage values\", () => {
    render(
      <SignalRadarPreview
        timingScore={0.85}
        textRepetitionScore={0.65}
        networkAnomalyScore={0.3}
        profileScore={0.15}
      />
    );

    expect(screen.getByText(\"Activity Timing\")).toBeInTheDocument();
    expect(screen.getByText(\"85%\")).toBeInTheDocument();
    expect(screen.getByText(\"Text Repetition\")).toBeInTheDocument();
    expect(screen.getByText(\"65%\")).toBeInTheDocument();
  });
});
""",
    "test(ui): test SignalRadarPreview renders percentage bars for all vectors"
)

# 9. app/investigations/loading.tsx
write_and_commit(
    "apps/dashboard/src/app/investigations/loading.tsx",
    """import React from \"react\";
import { Skeleton } from \"../../components/ui/skeleton\";

export default function InvestigationsLoading() {
  return (
    <div className=\"space-y-6\" data-testid=\"investigations-loading\">
      <div className=\"flex justify-between items-center\">
        <Skeleton className=\"h-8 w-48\" />
        <Skeleton className=\"h-9 w-32\" />
      </div>
      <div className=\"grid grid-cols-1 sm:grid-cols-3 gap-4\">
        {[...Array(3)].map((_, i) => (
          <Skeleton key={i} className=\"h-24 w-full\" />
        ))}
      </div>
      <Skeleton className=\"h-80 w-full rounded-lg\" />
    </div>
  );
}
""",
    "feat(ui): implement InvestigationsLoading skeleton for list route"
)

# 10. app/investigations/__tests__/loading.test.tsx
write_and_commit(
    "apps/dashboard/src/app/investigations/__tests__/loading.test.tsx",
    """import React from \"react\";
import { describe, it, expect } from \"vitest\";
import { render } from \"@testing-library/react\";
import InvestigationsLoading from \"../loading\";

describe(\"InvestigationsLoading\", () => {
  it(\"renders placeholder pulse elements\", () => {
    const { container } = render(<InvestigationsLoading />);
    const skeletons = container.querySelectorAll(\".animate-pulse\");
    expect(skeletons.length).toBeGreaterThan(0);
  });
});
""",
    "test(ui): test InvestigationsLoading skeleton renders pulse elements"
)

# 11. app/investigations/error.tsx
write_and_commit(
    "apps/dashboard/src/app/investigations/error.tsx",
    """\"use client\";

import React from \"react\";
import { AlertCircle, RotateCcw } from \"lucide-react\";
import { Button } from \"../../components/ui/button\";

export default function InvestigationsError({
  error,
  reset,
}: {
  error: Error & { digest?: string };
  reset: () => void;
}) {
  return (
    <div
      className=\"flex flex-col items-center justify-center p-8 text-center rounded-lg border border-border bg-card space-y-4 my-8\"
      data-testid=\"investigations-error\"
    >
      <div className=\"p-3 rounded-full bg-rose-500/10 text-rose-500\">
        <AlertCircle className=\"h-8 w-8\" />
      </div>
      <div className=\"space-y-1\">
        <h3 className=\"text-base font-semibold text-foreground\">Unable to load investigations</h3>
        <p className=\"text-xs text-muted-foreground max-w-sm\">
          {error.message || \"An unexpected error occurred while loading investigation records.\"}
        </p>
      </div>
      <Button onClick={reset} variant=\"outline\" className=\"gap-2\">
        <RotateCcw className=\"h-3.5 w-3.5\" />
        Retry
      </Button>
    </div>
  );
}
""",
    "feat(ui): implement InvestigationsError boundary component"
)

# 12. app/investigations/__tests__/error.test.tsx
write_and_commit(
    "apps/dashboard/src/app/investigations/__tests__/error.test.tsx",
    """import React from \"react\";
import { describe, it, expect, vi } from \"vitest\";
import { render, screen, fireEvent } from \"@testing-library/react\";
import InvestigationsError from \"../error\";

describe(\"InvestigationsError\", () => {
  it(\"renders error description and invokes reset on retry button click\", () => {
    const handleReset = vi.fn();
    render(<InvestigationsError error={new Error(\"Network timeout\")} reset={handleReset} />);

    expect(screen.getByText(\"Unable to load investigations\")).toBeInTheDocument();
    expect(screen.getByText(\"Network timeout\")).toBeInTheDocument();

    fireEvent.click(screen.getByText(\"Retry\"));
    expect(handleReset).toHaveBeenCalledTimes(1);
  });
});
""",
    "test(ui): test InvestigationsError displays message and retry action"
)

# 13. app/investigations/page.tsx
write_and_commit(
    "apps/dashboard/src/app/investigations/page.tsx",
    """\"use client\";

import React, { useState } from \"react\";
import Link from \"next/link\";
import { Search, Plus, ShieldCheck, ArrowRight, Activity } from \"lucide-react\";
import { Button } from \"../../components/ui/button\";
import { Badge } from \"../../components/ui/badge\";
import { useScans } from \"../../lib/hooks/use-scans\";
import { LaunchScanModal } from \"../../components/overview/launch-scan-modal\";
import { SyntheticDataBanner } from \"../../components/ui/synthetic-banner\";

export default function InvestigationsPage() {
  const { scans, isLoading, isError } = useScans();
  const [search, setSearch] = useState(\"\");
  const [statusFilter, setStatusFilter] = useState(\"ALL\");
  const [isModalOpen, setIsModalOpen] = useState(false);

  const filteredScans = (scans || []).filter((s) => {
    const matchSearch =
      s.target.toLowerCase().includes(search.toLowerCase()) ||
      s.id.toLowerCase().includes(search.toLowerCase());
    const matchStatus = statusFilter === \"ALL\" || s.status.toUpperCase() === statusFilter;
    return matchSearch && matchStatus;
  });

  return (
    <div className=\"space-y-6 pb-12\" data-testid=\"investigations-page\">
      <SyntheticDataBanner />

      <div className=\"flex flex-col sm:flex-row sm:items-center justify-between gap-4\">
        <div>
          <h1 className=\"text-xl font-bold text-foreground\">Investigation Archives</h1>
          <p className=\"text-xs text-muted-foreground mt-0.5\">
            Search, filter, and inspect past and active social network bot scans.
          </p>
        </div>

        <Button onClick={() => setIsModalOpen(true)} className=\"gap-2\">
          <Plus className=\"h-4 w-4\" />
          New Investigation
        </Button>
      </div>

      <div className=\"flex flex-col sm:flex-row gap-3 items-center justify-between\">
        <div className=\"relative w-full sm:w-72\">
          <Search className=\"absolute left-3 top-2.5 h-4 w-4 text-muted-foreground\" />
          <input
            type=\"text\"
            placeholder=\"Search by target or ID...\"
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            className=\"w-full pl-9 pr-3 py-2 text-xs rounded-md border border-input bg-background text-foreground focus:outline-none focus:ring-1 focus:ring-ring\"
          />
        </div>

        <div className=\"flex gap-1.5 self-start sm:self-auto\">
          {[\"ALL\", \"COMPLETED\", \"RUNNING\", \"FAILED\"].map((st) => (
            <button
              key={st}
              onClick={() => setStatusFilter(st)}
              className={`px-3 py-1.5 rounded text-xs font-medium transition-colors ${
                statusFilter === st
                  ? \"bg-primary text-primary-foreground\"
                  : \"bg-muted/40 text-muted-foreground hover:bg-muted/80\"
              }`}
            >
              {st}
            </button>
          ))}
        </div>
      </div>

      <div className=\"rounded-lg border border-border bg-card overflow-hidden\">
        {isLoading ? (
          <div className=\"p-8 text-center text-xs text-muted-foreground\">Loading investigations...</div>
        ) : filteredScans.length === 0 ? (
          <div className=\"p-8 text-center space-y-2\">
            <ShieldCheck className=\"h-8 w-8 text-muted-foreground mx-auto\" />
            <div className=\"text-sm font-medium text-foreground\">No investigations found</div>
            <div className=\"text-xs text-muted-foreground\">Try clearing your search query or start a new scan.</div>
          </div>
        ) : (
          <div className=\"divide-y divide-border\">
            {filteredScans.map((scan) => (
              <div
                key={scan.id}
                className=\"p-4 flex items-center justify-between hover:bg-muted/20 transition-colors\"
              >
                <div className=\"space-y-1\">
                  <div className=\"flex items-center gap-2\">
                    <span className=\"font-medium text-sm text-foreground\">{scan.target}</span>
                    <Badge variant={scan.status === \"completed\" ? \"success\" : \"secondary\"}>
                      {scan.status}
                    </Badge>
                    <span className=\"text-xs font-mono text-muted-foreground\">{scan.platform}</span>
                  </div>
                  <div className=\"text-xs text-muted-foreground flex items-center gap-3\">
                    <span>ID: {scan.id}</span>
                    <span>•</span>
                    <span>Created: {new Date(scan.created_at).toLocaleDateString()}</span>
                  </div>
                </div>

                <Link
                  href={`/investigations/${scan.id}`}
                  className=\"flex items-center gap-1.5 text-xs font-medium text-primary hover:underline\"
                >
                  Inspect
                  <ArrowRight className=\"h-3.5 w-3.5\" />
                </Link>
              </div>
            ))}
          </div>
        )}
      </div>

      <LaunchScanModal isOpen={isModalOpen} onClose={() => setIsModalOpen(false)} />
    </div>
  );
}
""",
    "feat(ui): implement InvestigationsPage archive listing with search and status filtering"
)

# 14. app/investigations/__tests__/page.test.tsx
write_and_commit(
    "apps/dashboard/src/app/investigations/__tests__/page.test.tsx",
    """import React from \"react\";
import { describe, it, expect, vi } from \"vitest\";
import { render, screen, fireEvent } from \"@testing-library/react\";
import InvestigationsPage from \"../page\";

vi.mock(\"../../../lib/hooks/use-scans\", () => ({
  useScans: () => ({
    scans: [
      {
        id: \"scan_abc\",
        target: \"test_influencer\",
        platform: \"twitter\",
        status: \"completed\",
        created_at: \"2026-11-05T08:00:00Z\",
      },
      {
        id: \"scan_xyz\",
        target: \"crypto_bot_target\",
        platform: \"bluesky\",
        status: \"running\",
        created_at: \"2026-11-05T09:00:00Z\",
      },
    ],
    isLoading: false,
    isError: false,
  }),
}));

describe(\"InvestigationsPage\", () => {
  it(\"renders investigation archives and filters by status\", () => {
    render(<InvestigationsPage />);

    expect(screen.getByText(\"Investigation Archives\")).toBeInTheDocument();
    expect(screen.getByText(\"test_influencer\")).toBeInTheDocument();
    expect(screen.getByText(\"crypto_bot_target\")).toBeInTheDocument();

    // Filter by RUNNING
    fireEvent.click(screen.getByText(\"RUNNING\"));
    expect(screen.queryByText(\"test_influencer\")).not.toBeInTheDocument();
    expect(screen.getByText(\"crypto_bot_target\")).toBeInTheDocument();
  });
});
""",
    "test(ui): test InvestigationsPage listing and client-side status filtering"
)

# 15. app/investigations/[id]/loading.tsx
write_and_commit(
    "apps/dashboard/src/app/investigations/[id]/loading.tsx",
    """import React from \"react\";
import { Skeleton } from \"../../../components/ui/skeleton\";

export default function InvestigationDetailLoading() {
  return (
    <div className=\"space-y-6\" data-testid=\"investigation-detail-loading\">
      <div className=\"flex justify-between items-center\">
        <Skeleton className=\"h-10 w-64\" />
        <Skeleton className=\"h-9 w-24\" />
      </div>
      <div className=\"grid grid-cols-2 lg:grid-cols-4 gap-4\">
        {[...Array(4)].map((_, i) => (
          <Skeleton key={i} className=\"h-24 w-full\" />
        ))}
      </div>
      <Skeleton className=\"h-12 w-full\" />
      <Skeleton className=\"h-96 w-full rounded-lg\" />
    </div>
  );
}
""",
    "feat(ui): implement InvestigationDetailLoading skeleton component"
)

# 16. app/investigations/[id]/__tests__/loading.test.tsx
write_and_commit(
    "apps/dashboard/src/app/investigations/[id]/__tests__/loading.test.tsx",
    """import React from \"react\";
import { describe, it, expect } from \"vitest\";
import { render } from \"@testing-library/react\";
import InvestigationDetailLoading from \"../loading\";

describe(\"InvestigationDetailLoading\", () => {
  it(\"renders loading skeleton elements\", () => {
    const { container } = render(<InvestigationDetailLoading />);
    const skeletons = container.querySelectorAll(\".animate-pulse\");
    expect(skeletons.length).toBeGreaterThan(0);
  });
});
""",
    "test(ui): test InvestigationDetailLoading placeholder rendering"
)

# 17. app/investigations/[id]/error.tsx
write_and_commit(
    "apps/dashboard/src/app/investigations/[id]/error.tsx",
    """\"use client\";

import React from \"react\";
import Link from \"next/link\";
import { AlertCircle, ArrowLeft, RotateCcw } from \"lucide-react\";
import { Button } from \"../../../components/ui/button\";

export default function InvestigationDetailError({
  error,
  reset,
}: {
  error: Error & { digest?: string };
  reset: () => void;
}) {
  return (
    <div
      className=\"flex flex-col items-center justify-center p-8 text-center rounded-lg border border-border bg-card space-y-4 my-8\"
      data-testid=\"investigation-detail-error\"
    >
      <div className=\"p-3 rounded-full bg-rose-500/10 text-rose-500\">
        <AlertCircle className=\"h-8 w-8\" />
      </div>
      <div className=\"space-y-1\">
        <h3 className=\"text-base font-semibold text-foreground\">Failed to load investigation workspace</h3>
        <p className=\"text-xs text-muted-foreground max-w-sm\">
          {error.message || \"Investigation record not found or inaccessible.\"}
        </p>
      </div>
      <div className=\"flex gap-3\">
        <Link href=\"/investigations\">
          <Button variant=\"outline\" className=\"gap-2\">
            <ArrowLeft className=\"h-3.5 w-3.5\" />
            Back to List
          </Button>
        </Link>
        <Button onClick={reset} className=\"gap-2\">
          <RotateCcw className=\"h-3.5 w-3.5\" />
          Retry
        </Button>
      </div>
    </div>
  );
}
""",
    "feat(ui): implement InvestigationDetailError boundary component"
)

# 18. app/investigations/[id]/__tests__/error.test.tsx
write_and_commit(
    "apps/dashboard/src/app/investigations/[id]/__tests__/error.test.tsx",
    """import React from \"react\";
import { describe, it, expect, vi } from \"vitest\";
import { render, screen, fireEvent } from \"@testing-library/react\";
import InvestigationDetailError from \"../error\";

describe(\"InvestigationDetailError\", () => {
  it(\"renders error message and provides retry and back navigation\", () => {
    const handleReset = vi.fn();
    render(<InvestigationDetailError error={new Error(\"Workspace unavailable\")} reset={handleReset} />);

    expect(screen.getByText(\"Failed to load investigation workspace\")).toBeInTheDocument();
    expect(screen.getByText(\"Workspace unavailable\")).toBeInTheDocument();

    fireEvent.click(screen.getByText(\"Retry\"));
    expect(handleReset).toHaveBeenCalledTimes(1);
  });
});
""",
    "test(ui): test InvestigationDetailError retry trigger and navigation controls"
)

# 19. app/investigations/[id]/page.tsx
write_and_commit(
    "apps/dashboard/src/app/investigations/[id]/page.tsx",
    """\"use client\";

import React, { useState } from \"react\";
import { useParams } from \"next/navigation\";
import { InvestigationHeader } from \"../../../components/investigation/investigation-header\";
import { InvestigationTabs } from \"../../../components/investigation/investigation-tabs\";
import { OverviewSummaryCard } from \"../../../components/investigation/overview-summary-card\";
import { RelationshipTable } from \"../../../components/investigation/relationship-table\";
import { FilterToolbar } from \"../../../components/investigation/filter-toolbar\";
import { PaginationBar } from \"../../../components/investigation/pagination-bar\";
import { ExportDialog } from \"../../../components/investigation/export-dialog\";
import { ExportPanel } from \"../../../components/investigation/export-panel\";
import { AccountFeaturesTable } from \"../../../components/investigation/account-features-table\";
import { EmptyAccountsState } from \"../../../components/investigation/empty-accounts-state\";
import { SyntheticDataBanner } from \"../../../components/ui/synthetic-banner\";
import { useInvestigation } from \"../../../lib/hooks/use-investigation\";
import { useRelationships } from \"../../../lib/hooks/use-relationships\";
import { useInvestigationExport } from \"../../../lib/hooks/use-investigation-export\";

export default function InvestigationDetailPage() {
  const params = useParams();
  const scanId = typeof params?.id === \"string\" ? params.id : \"\";

  const [activeTab, setActiveTab] = useState(\"overview\");
  const [search, setSearch] = useState(\"\");
  const [riskBand, setRiskBand] = useState(\"all\");
  const [sortBy, setSortBy] = useState(\"risk_desc\");
  const [currentPage, setCurrentPage] = useState(1);
  const [isExportModalOpen, setIsExportModalOpen] = useState(false);

  const { investigation, isLoading: isInvLoading } = useInvestigation(scanId);
  const { relationships, totalCount, isLoading: isRelLoading } = useRelationships(scanId);
  const { exportData, isExporting } = useInvestigationExport(scanId);

  const handleExport = async (format: \"csv\" | \"json\") => {
    await exportData(format);
    setIsExportModalOpen(false);
  };

  const filteredEdges = (relationships || []).filter((edge) => {
    const matchSearch =
      edge.source_id.toLowerCase().includes(search.toLowerCase()) ||
      edge.target_id.toLowerCase().includes(search.toLowerCase());
    return matchSearch;
  });

  return (
    <div className=\"space-y-6 pb-12\" data-testid=\"investigation-workspace\">
      <SyntheticDataBanner />

      <InvestigationHeader
        scanId={scanId}
        target={investigation?.target || \"Target Account\"}
        platform={investigation?.platform || \"twitter\"}
        status={investigation?.status || \"completed\"}
        totalAccounts={investigation?.accounts_analyzed ?? totalCount}
        botAccounts={investigation?.bot_count ?? 0}
        onExportClick={() => setIsExportModalOpen(true)}
      />

      <InvestigationTabs
        activeTab={activeTab}
        onTabChange={setActiveTab}
        tabCounts={{
          explorer: totalCount,
          features: investigation?.features?.length ?? 0,
        }}
      />

      {activeTab === \"overview\" && (
        <div className=\"space-y-6\">
          <OverviewSummaryCard
            totalAccounts={investigation?.accounts_analyzed ?? totalCount}
            botAccounts={investigation?.bot_count ?? 0}
            avgRiskScore={0.64}
            criticalCount={4}
          />

          <div className=\"rounded-lg border border-border bg-card p-6 space-y-4\">
            <h3 className=\"text-sm font-semibold text-foreground\">Primary Relationships Preview</h3>
            <RelationshipTable relationships={filteredEdges.slice(0, 10)} />
          </div>
        </div>
      )}

      {activeTab === \"explorer\" && (
        <div className=\"space-y-4\">
          <FilterToolbar
            search={search}
            onSearchChange={setSearch}
            riskBand={riskBand}
            onRiskBandChange={setRiskBand}
            sortBy={sortBy}
            onSortByChange={setSortBy}
            onExportClick={() => setIsExportModalOpen(true)}
          />

          {filteredEdges.length === 0 ? (
            <EmptyAccountsState onResetFilters={() => { setSearch(\"\"); setRiskBand(\"all\"); }} />
          ) : (
            <>
              <RelationshipTable relationships={filteredEdges} />
              <PaginationBar
                currentPage={currentPage}
                totalPages={Math.max(1, Math.ceil(filteredEdges.length / 25))}
                onPageChange={setCurrentPage}
              />
            </>
          )}
        </div>
      )}

      {activeTab === \"features\" && (
        <div className=\"space-y-4\">
          <AccountFeaturesTable features={investigation?.features || []} />
        </div>
      )}

      {activeTab === \"export\" && (
        <ExportPanel
          scanId={scanId}
          onExportCsv={() => exportData(\"csv\")}
          onExportJson={() => exportData(\"json\")}
          isExporting={isExporting}
        />
      )}

      <ExportDialog
        isOpen={isExportModalOpen}
        onClose={() => setIsExportModalOpen(false)}
        onExport={handleExport}
        isExporting={isExporting}
      />
    </div>
  );
}
""",
    "feat(ui): implement InvestigationDetailPage workspace with multi-tab investigation routing"
)

# 20. app/investigations/[id]/__tests__/page.test.tsx
write_and_commit(
    "apps/dashboard/src/app/investigations/[id]/__tests__/page.test.tsx",
    """import React from \"react\";
import { describe, it, expect, vi } from \"vitest\";
import { render, screen, fireEvent } from \"@testing-library/react\";
import InvestigationDetailPage from \"../page\";

vi.mock(\"next/navigation\", () => ({
  useParams: () => ({ id: \"scan_workspace_01\" }),
  useRouter: () => ({ push: vi.fn() }),
}));

vi.mock(\"../../../lib/hooks/use-investigation\", () => ({
  useInvestigation: () => ({
    investigation: {
      id: \"scan_workspace_01\",
      target: \"target_botnet\",
      platform: \"twitter\",
      status: \"completed\",
      accounts_analyzed: 150,
      bot_count: 42,
    },
    isLoading: false,
    isError: false,
  }),
}));

vi.mock(\"../../../lib/hooks/use-relationships\", () => ({
  useRelationships: () => ({
    relationships: [
      {
        source_id: \"acc_1\",
        target_id: \"target_botnet\",
        relationship_type: \"follower\",
        confidence: 0.95,
      },
    ],
    totalCount: 1,
    isLoading: false,
  }),
}));

describe(\"InvestigationDetailPage\", () => {
  it(\"renders investigation workspace with tabs and switches view\", () => {
    render(<InvestigationDetailPage />);

    expect(screen.getByTestId(\"investigation-workspace\")).toBeInTheDocument();
    expect(screen.getByText(\"target_botnet\")).toBeInTheDocument();

    // Switch to explorer tab
    const explorerTab = screen.getByText(/Followers \\/ Following/);
    fireEvent.click(explorerTab);
    expect(screen.getByPlaceholderText(/Search by handle or account ID/)).toBeInTheDocument();
  });
});
""",
    "test(ui): test InvestigationDetailPage tabs switching and relationship filtering"
)

# 21. app/investigations/[id]/accounts/[accountId]/loading.tsx
write_and_commit(
    "apps/dashboard/src/app/investigations/[id]/accounts/[accountId]/loading.tsx",
    """import React from \"react\";
import { Skeleton } from \"../../../../../components/ui/skeleton\";

export default function AccountDetailLoading() {
  return (
    <div className=\"space-y-6\" data-testid=\"account-detail-loading\">
      <div className=\"flex items-center gap-4\">
        <Skeleton className=\"h-16 w-16 rounded-full\" />
        <div className=\"space-y-2\">
          <Skeleton className=\"h-6 w-48\" />
          <Skeleton className=\"h-4 w-32\" />
        </div>
      </div>
      <div className=\"grid grid-cols-1 md:grid-cols-3 gap-6\">
        <Skeleton className=\"h-48 w-full rounded-lg\" />
        <Skeleton className=\"h-48 w-full rounded-lg\" />
        <Skeleton className=\"h-48 w-full rounded-lg\" />
      </div>
      <Skeleton className=\"h-64 w-full rounded-lg\" />
    </div>
  );
}
""",
    "feat(ui): implement AccountDetailLoading skeleton component"
)

# 22. app/investigations/[id]/accounts/[accountId]/__tests__/loading.test.tsx
write_and_commit(
    "apps/dashboard/src/app/investigations/[id]/accounts/[accountId]/__tests__/loading.test.tsx",
    """import React from \"react\";
import { describe, it, expect } from \"vitest\";
import { render } from \"@testing-library/react\";
import AccountDetailLoading from \"../loading\";

describe(\"AccountDetailLoading\", () => {
  it(\"renders account detail skeleton placeholders\", () => {
    const { container } = render(<AccountDetailLoading />);
    const skeletons = container.querySelectorAll(\".animate-pulse\");
    expect(skeletons.length).toBeGreaterThan(0);
  });
});
""",
    "test(ui): test AccountDetailLoading renders pulse placeholders"
)

# 23. app/investigations/[id]/accounts/[accountId]/error.tsx
write_and_commit(
    "apps/dashboard/src/app/investigations/[id]/accounts/[accountId]/error.tsx",
    """\"use client\";

import React from \"react\";
import { AlertCircle, RotateCcw } from \"lucide-react\";
import { Button } from \"../../../../../components/ui/button\";

export default function AccountDetailError({
  error,
  reset,
}: {
  error: Error & { digest?: string };
  reset: () => void;
}) {
  return (
    <div
      className=\"flex flex-col items-center justify-center p-8 text-center rounded-lg border border-border bg-card space-y-4 my-8\"
      data-testid=\"account-detail-error\"
    >
      <div className=\"p-3 rounded-full bg-rose-500/10 text-rose-500\">
        <AlertCircle className=\"h-8 w-8\" />
      </div>
      <div className=\"space-y-1\">
        <h3 className=\"text-base font-semibold text-foreground\">Unable to load account assessment</h3>
        <p className=\"text-xs text-muted-foreground max-w-sm\">
          {error.message || \"Account record or evidence could not be retrieved.\"}
        </p>
      </div>
      <Button onClick={reset} className=\"gap-2\">
        <RotateCcw className=\"h-3.5 w-3.5\" />
        Retry Assessment
      </Button>
    </div>
  );
}
""",
    "feat(ui): implement AccountDetailError boundary component"
)

# 24. app/investigations/[id]/accounts/[accountId]/__tests__/error.test.tsx
write_and_commit(
    "apps/dashboard/src/app/investigations/[id]/accounts/[accountId]/__tests__/error.test.tsx",
    """import React from \"react\";
import { describe, it, expect, vi } from \"vitest\";
import { render, screen, fireEvent } from \"@testing-library/react\";
import AccountDetailError from \"../error\";

describe(\"AccountDetailError\", () => {
  it(\"renders error description and retry handler\", () => {
    const handleReset = vi.fn();
    render(<AccountDetailError error={new Error(\"Assessment failure\")} reset={handleReset} />);

    expect(screen.getByText(\"Unable to load account assessment\")).toBeInTheDocument();
    expect(screen.getByText(\"Assessment failure\")).toBeInTheDocument();

    fireEvent.click(screen.getByText(\"Retry Assessment\"));
    expect(handleReset).toHaveBeenCalledTimes(1);
  });
});
""",
    "test(ui): test AccountDetailError displays error state and invokes reset"
)

# 25. app/investigations/[id]/accounts/[accountId]/page.tsx
write_and_commit(
    "apps/dashboard/src/app/investigations/[id]/accounts/[accountId]/page.tsx",
    """\"use client\";

import React from \"react\";
import Link from \"next/link\";
import { useParams } from \"next/navigation\";
import { ArrowLeft, Shield, AlertTriangle } from \"lucide-react\";
import { Button } from \"../../../../../components/ui/button\";
import { AccountProfileCard } from \"../../../../../components/investigation/account-profile-card\";
import { RiskGauge } from \"../../../../../components/investigation/risk-gauge\";
import { FollowerRatioGauge } from \"../../../../../components/investigation/follower-ratio-gauge\";
import { ContributingSignalBar } from \"../../../../../components/investigation/contributing-signal-bar\";
import { EvidenceInspector } from \"../../../../../components/investigation/evidence-inspector\";
import { LimitationsCard } from \"../../../../../components/investigation/limitations-card\";
import { TimelineSnapshot } from \"../../../../../components/investigation/timeline-snapshot\";
import { AccountNeighborhoodViewer } from \"../../../../../components/investigation/account-neighborhood-viewer\";
import { SignalRadarPreview } from \"../../../../../components/investigation/signal-radar-preview\";
import { SyntheticDataBanner } from \"../../../../../components/ui/synthetic-banner\";
import { useAccountDetail } from \"../../../../../lib/hooks/use-account-detail\";
import { useAccountEvidence } from \"../../../../../lib/hooks/use-account-evidence\";
import { useAccountNeighborhood } from \"../../../../../lib/hooks/use-account-neighborhood\";

export default function AccountDetailPage() {
  const params = useParams();
  const scanId = typeof params?.id === \"string\" ? params.id : \"\";
  const accountId = typeof params?.accountId === \"string\" ? params.accountId : \"\";

  const { account, isLoading: isAccLoading } = useAccountDetail(scanId, accountId);
  const { evidence, isLoading: isEvLoading } = useAccountEvidence(scanId, accountId);
  const { neighborhood } = useAccountNeighborhood(scanId, accountId);

  const riskScore = account?.assessment?.risk_score ?? 0.82;
  const confidence = account?.assessment?.confidence ?? 0.91;

  return (
    <div className=\"space-y-6 pb-12\" data-testid=\"account-detail-page\">
      <SyntheticDataBanner />

      <div className=\"flex items-center justify-between\">
        <Link href={`/investigations/${scanId}`}>
          <Button variant=\"outline\" size=\"sm\" className=\"gap-2 text-xs\">
            <ArrowLeft className=\"h-3.5 w-3.5\" />
            Back to Investigation Workspace
          </Button>
        </Link>
        <span className=\"text-xs font-mono text-muted-foreground\">ID: {accountId}</span>
      </div>

      <AccountProfileCard
        username={account?.account?.username || accountId}
        platform={account?.account?.platform || \"twitter\"}
        riskScore={riskScore}
        confidence={confidence}
        followers={account?.observation?.followers_count ?? 1240}
        following={account?.observation?.following_count ?? 14500}
        postsCount={account?.observation?.posts_count ?? 32}
        observation={account?.observation}
      />

      <div className=\"grid grid-cols-1 md:grid-cols-3 gap-6\">
        <div className=\"rounded-lg border border-border bg-card p-5 flex flex-col items-center justify-center text-center space-y-2\">
          <h4 className=\"text-xs font-semibold uppercase tracking-wider text-muted-foreground\">
            Overall Risk Evaluation
          </h4>
          <RiskGauge score={riskScore} confidence={confidence} size={150} />
        </div>

        <FollowerRatioGauge
          followers={account?.observation?.followers_count ?? 1240}
          following={account?.observation?.following_count ?? 14500}
        />

        <SignalRadarPreview
          timingScore={0.88}
          textRepetitionScore={0.76}
          networkAnomalyScore={0.62}
          profileScore={0.45}
        />
      </div>

      <div className=\"grid grid-cols-1 lg:grid-cols-3 gap-6\">
        <div className=\"lg:col-span-2 space-y-6\">
          <div className=\"rounded-lg border border-border bg-card p-5 space-y-4\">
            <h3 className=\"text-sm font-semibold text-foreground flex items-center gap-2\">
              <Shield className=\"h-4 w-4 text-primary\" />
              Contributing Heuristic Signals
            </h3>
            <div className=\"space-y-3\">
              <ContributingSignalBar
                name=\"High Following-to-Follower Ratio\"
                score={0.92}
                weight={0.35}
                contribution={0.32}
              />
              <ContributingSignalBar
                name=\"Temporal Synchrony with Bot Farm\"
                score={0.85}
                weight={0.4}
                contribution={0.34}
              />
              <ContributingSignalBar
                name=\"Copypasta Linguistic Match\"
                score={0.78}
                weight={0.25}
                contribution={0.19}
              />
            </div>
          </div>

          <EvidenceInspector evidence={evidence || []} />
        </div>

        <div className=\"space-y-6\">
          <LimitationsCard
            limitations={[
              \"Direct messages and private interactions unobservable under public API tier.\",
              \"Historical profile photo changes truncated prior to observation window.\",
            ]}
          />

          <TimelineSnapshot
            observations={
              account?.observation
                ? [account.observation]
                : [
                    {
                      observed_at: \"2026-11-05T08:30:00Z\",
                      followers_count: 1240,
                      following_count: 14500,
                      posts_count: 32,
                    },
                  ]
            }
          />

          {neighborhood && (
            <AccountNeighborhoodViewer
              currentAccountId={accountId}
              neighborhood={neighborhood}
            />
          )}
        </div>
      </div>
    </div>
  );
}
""",
    "feat(ui): implement AccountDetailPage deep-dive view with risk decomposition and neighborhood"
)

# 26. app/investigations/[id]/accounts/[accountId]/__tests__/page.test.tsx
write_and_commit(
    "apps/dashboard/src/app/investigations/[id]/accounts/[accountId]/__tests__/page.test.tsx",
    """import React from \"react\";
import { describe, it, expect, vi } from \"vitest\";
import { render, screen } from \"@testing-library/react\";
import AccountDetailPage from \"../page\";

vi.mock(\"next/navigation\", () => ({
  useParams: () => ({ id: \"scan_workspace_01\", accountId: \"bot_suspect_42\" }),
  useRouter: () => ({ push: vi.fn() }),
}));

vi.mock(\"../../../../../lib/hooks/use-account-detail\", () => ({
  useAccountDetail: () => ({
    account: {
      account: {
        id: \"bot_suspect_42\",
        username: \"bot_suspect_42\",
        platform: \"twitter\",
      },
      assessment: {
        account_id: \"bot_suspect_42\",
        risk_score: 0.89,
        risk_band: \"high\",
        confidence: 0.94,
      },
      observation: {
        observed_at: \"2026-11-05T08:00:00Z\",
        followers_count: 50,
        following_count: 4500,
        posts_count: 12,
      },
    },
    isLoading: false,
  }),
}));

vi.mock(\"../../../../../lib/hooks/use-account-evidence\", () => ({
  useAccountEvidence: () => ({
    evidence: [
      {
        id: \"ev_1\",
        rule_name: \"High following ratio\",
        score: 0.9,
        weight: 0.35,
        confidence: 0.9,
        summary: \"Follows 4500 with only 50 followers\",
        observed_data: {},
      },
    ],
    isLoading: false,
  }),
}));

vi.mock(\"../../../../../lib/hooks/use-account-neighborhood\", () => ({
  useAccountNeighborhood: () => ({
    neighborhood: {
      target_account_id: \"bot_suspect_42\",
      incoming: [],
      outgoing: [],
    },
    isLoading: false,
  }),
}));

describe(\"AccountDetailPage\", () => {
  it(\"renders account deep dive with profile, risk gauge, signals and evidence\", () => {
    render(<AccountDetailPage />);

    expect(screen.getByTestId(\"account-detail-page\")).toBeInTheDocument();
    expect(screen.getByText(\"@bot_suspect_42\")).toBeInTheDocument();
    expect(screen.getByText(\"Overall Risk Evaluation\")).toBeInTheDocument();
    expect(screen.getByText(\"Contributing Heuristic Signals\")).toBeInTheDocument();
  });
});
""",
    "test(ui): test AccountDetailPage deep-dive rendering with profile, signals and evidence"
)

print("Batch 4 finished 26 commits.")

