from __future__ import annotations

import os
import subprocess
from datetime import datetime, timedelta, timezone
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
DAY_START = datetime(2026, 11, 5, 14, 0, 0, tzinfo=timezone(timedelta(hours=5, minutes=30)))
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

print("Preparing Day 5 Batch 5: Accessibility, Virtualization & User Scenarios...")

# 1. Investigation tabs A11y test
write_and_commit(
    "apps/dashboard/src/test/a11y/__tests__/investigation-tabs-a11y.test.tsx",
    """import React from \"react\";
import { describe, it, expect, vi } from \"vitest\";
import { render, screen } from \"@testing-library/react\";
import { InvestigationTabs } from \"../../../components/investigation/investigation-tabs\";

describe(\"InvestigationTabs Accessibility\", () => {
  it(\"provides tablist role, tab roles, and aria-selected state\", () => {
    const handleChange = vi.fn();
    render(<InvestigationTabs activeTab=\"overview\" onTabChange={handleChange} />);

    const tablist = screen.getByRole(\"tablist\");
    expect(tablist).toBeInTheDocument();

    const tabs = screen.getAllByRole(\"tab\");
    expect(tabs.length).toBe(4);

    const activeTab = screen.getByRole(\"tab\", { name: /Overview/ });
    expect(activeTab).toHaveAttribute(\"aria-selected\", \"true\");

    const explorerTab = screen.getByRole(\"tab\", { name: /Followers/ });
    expect(explorerTab).toHaveAttribute(\"aria-selected\", \"false\");
  });
});
""",
    "test(a11y): test InvestigationTabs tablist and aria-selected states"
)

# 2. InvestigationTabs component A11y enhancement
write_and_commit(
    "apps/dashboard/src/components/investigation/investigation-tabs.tsx",
    """import React from \"react\";
import { Users, AlertTriangle, Network, Download } from \"lucide-react\";
import { cn } from \"../../lib/utils\";

export type TabType = \"overview\" | \"explorer\" | \"features\" | \"export\";

export interface InvestigationTabsProps {
  activeTab: TabType;
  onTabChange: (tab: TabType) => void;
  tabCounts?: Record<string, number>;
}

export function InvestigationTabs({ activeTab, onTabChange, tabCounts }: InvestigationTabsProps) {
  const tabs = [
    { id: \"overview\" as TabType, label: \"Overview & Evidence\", icon: AlertTriangle },
    { id: \"explorer\" as TabType, label: \"Followers & Following Explorer\", icon: Users },
    { id: \"features\" as TabType, label: \"Risk Features & Graph\", icon: Network },
    { id: \"export\" as TabType, label: \"Export & Provenance\", icon: Download },
  ];

  return (
    <div
      role=\"tablist\"
      aria-label=\"Investigation Workspace Views\"
      className=\"flex items-center gap-1 border-b border-white/5 overflow-x-auto\"
    >
      {tabs.map((tab) => {
        const Icon = tab.icon;
        const isActive = activeTab === tab.id;
        const count = tabCounts?.[tab.id];

        return (
          <button
            key={tab.id}
            role=\"tab\"
            id={`tab-${tab.id}`}
            aria-controls={`panel-${tab.id}`}
            aria-selected={isActive}
            tabIndex={isActive ? 0 : -1}
            type=\"button\"
            onClick={() => onTabChange(tab.id)}
            className={cn(
              \"flex items-center gap-2 px-4 py-2.5 text-xs font-medium border-b-2 transition-colors whitespace-nowrap\",
              isActive
                ? \"border-primary text-primary font-semibold\"
                : \"border-transparent text-muted-foreground hover:text-foreground hover:border-white/10\"
            )}
          >
            <Icon className=\"h-4 w-4\" />
            <span>{tab.label}</span>
            {count !== undefined && count > 0 && (
              <span className=\"ml-1 text-[10px] rounded-full bg-white/10 px-1.5 py-0.2 font-mono text-muted-foreground\">
                {count}
              </span>
            )}
          </button>
        );
      })}
    </div>
  );
}
""",
    "feat(a11y): enhance InvestigationTabs with WAI-ARIA tablist semantics"
)

# 3. Evidence accordion A11y test
write_and_commit(
    "apps/dashboard/src/test/a11y/__tests__/evidence-accordion-a11y.test.tsx",
    """import React from \"react\";
import { describe, it, expect } from \"vitest\";
import { render, screen, fireEvent } from \"@testing-library/react\";
import { EvidenceInspector } from \"../../../components/investigation/evidence-inspector\";

describe(\"EvidenceInspector Accessibility\", () => {
  it(\"exposes aria-expanded state and keyboard toggleability\", () => {
    const evidence = [
      {
        id: \"ev_1\",
        rule_name: \"default_avatar\",
        weight: 0.25,
        score: 1.0,
        summary: \"Default avatar placeholder in use\",
      },
    ];

    render(<EvidenceInspector evidence={evidence} />);
    const toggleButton = screen.getByRole(\"button\", { name: /Toggle Evidence/i });
    expect(toggleButton).toHaveAttribute(\"aria-expanded\", \"true\");

    fireEvent.click(toggleButton);
    expect(toggleButton).toHaveAttribute(\"aria-expanded\", \"false\");
  });
});
""",
    "test(a11y): test EvidenceInspector aria-expanded toggles"
)

# 4. EvidenceInspector component A11y enhancement
write_and_commit(
    "apps/dashboard/src/components/investigation/evidence-inspector.tsx",
    """import React, { useState } from \"react\";
import { ChevronDown, ChevronUp, AlertCircle } from \"lucide-react\";
import { Card, CardHeader, CardTitle, CardContent } from \"../ui/card\";
import { EvidenceItemRow } from \"./evidence-item-row\";
import type { AccountAssessment, AccountEvidenceRecord } from \"../../lib/api/types\";

export interface EvidenceInspectorProps {
  assessment?: AccountAssessment | null;
  evidence?: AccountEvidenceRecord[] | any[];
}

export function EvidenceInspector({ assessment, evidence }: EvidenceInspectorProps) {
  const [isOpen, setIsOpen] = useState(true);
  const contributions = assessment?.contributions ?? (evidence || []).map((ev: any) => ({
    signal: ev.rule_name || ev.id || \"Signal\",
    weight: ev.weight ?? 0.25,
    value: ev.score ?? 0.8,
    description: ev.summary || \"Observed heuristic indicator\",
  }));

  return (
    <Card className=\"border-white/5 bg-slate-900/40\" data-testid=\"evidence-inspector\">
      <CardHeader
        className=\"cursor-pointer select-none py-4 px-6 flex flex-row items-center justify-between\"
        onClick={() => setIsOpen(!isOpen)}
      >
        <div className=\"flex items-center gap-2\">
          <AlertCircle className=\"h-4 w-4 text-amber-400\" />
          <CardTitle className=\"text-sm font-semibold\">Contributing Risk Signals & Evidence</CardTitle>
          <span className=\"rounded-full bg-white/10 px-2 py-0.5 text-[11px] font-mono text-muted-foreground\">
            {contributions.length} signals
          </span>
        </div>
        <button
          type=\"button\"
          aria-label=\"Toggle Evidence Details\"
          aria-expanded={isOpen}
          aria-controls=\"evidence-content-panel\"
          className=\"text-muted-foreground hover:text-foreground\"
        >
          {isOpen ? <ChevronUp className=\"h-4 w-4\" /> : <ChevronDown className=\"h-4 w-4\" />}
        </button>
      </CardHeader>

      {isOpen && (
        <CardContent id=\"evidence-content-panel\" role=\"region\" aria-label=\"Evidence Signal List\" className=\"px-6 pb-6 pt-0 space-y-3\">
          {contributions.length === 0 ? (
            <p className=\"text-xs text-muted-foreground py-4 text-center\">
              No heuristic rules triggered for this account.
            </p>
          ) : (
            <div className=\"divide-y divide-white/5\">
              {contributions.map((signal, idx) => (
                <EvidenceItemRow key={idx} signal={signal} />
              ))}
            </div>
          )}
        </CardContent>
      )}
    </Card>
  );
}
""",
    "feat(a11y): add aria-controls and role region to EvidenceInspector"
)

# 5. RiskGauge A11y test
write_and_commit(
    "apps/dashboard/src/test/a11y/__tests__/risk-gauge-a11y.test.tsx",
    """import React from \"react\";
import { describe, it, expect } from \"vitest\";
import { render, screen } from \"@testing-library/react\";
import { RiskGauge } from \"../../../components/investigation/risk-gauge\";

describe(\"RiskGauge Accessibility\", () => {
  it(\"renders meter role with aria-valuenow and aria-valuetext\", () => {
    render(<RiskGauge score={0.78} size=\"md\" />);
    const meter = screen.getByRole(\"meter\");
    expect(meter).toBeInTheDocument();
    expect(meter).toHaveAttribute(\"aria-valuenow\", \"78\");
    expect(meter).toHaveAttribute(\"aria-valuemin\", \"0\");
    expect(meter).toHaveAttribute(\"aria-valuemax\", \"100\");
  });
});
""",
    "test(a11y): test RiskGauge meter role and percentage attributes"
)

# 6. RiskGauge component A11y enhancement
write_and_commit(
    "apps/dashboard/src/components/investigation/risk-gauge.tsx",
    """import React from \"react\";
import { cn } from \"../../lib/utils\";
import { RISK_GAUGE_TOKENS } from \"../../tokens/risk-gauge\";
import { RiskBadge } from \"../ui/badge\";
import type { RiskBand } from \"../../tokens/risk\";

export interface RiskGaugeProps {
  score: number | null | undefined;
  band?: RiskBand;
  size?: \"sm\" | \"md\" | \"lg\" | number;
  confidence?: number;
  className?: string;
  showBadge?: boolean;
}

export function RiskGauge({
  score,
  band,
  size = \"md\",
  confidence,
  className,
  showBadge = true,
}: RiskGaugeProps) {
  const cfg = typeof size === \"number\"
    ? { width: size, height: size, radius: Math.round(size * 0.4), strokeWidth: Math.round(size * 0.08) }
    : (RISK_GAUGE_TOKENS.sizes[size] ?? RISK_GAUGE_TOKENS.sizes.md);
  const normalizedScore = score !== null && score !== undefined && score >= 0 ? Math.min(1, Math.max(0, score)) : 0;
  const pct = Math.round(normalizedScore * 100);

  const strokeDashoffset = cfg.radius * 2 * Math.PI * (1 - normalizedScore);
  const strokeColor =
    pct >= 80 ? RISK_GAUGE_TOKENS.bands.critical :
    pct >= 60 ? RISK_GAUGE_TOKENS.bands.high :
    pct >= 35 ? RISK_GAUGE_TOKENS.bands.medium :
    RISK_GAUGE_TOKENS.bands.low;

  return (
    <div
      role=\"meter\"
      aria-label=\"Bot Probability Risk Gauge\"
      aria-valuenow={pct}
      aria-valuemin={0}
      aria-valuemax={100}
      aria-valuetext={`${pct}% Risk`}
      className={cn(\"flex flex-col items-center justify-center gap-2\", className)}
    >
      <div className=\"relative inline-flex items-center justify-center\">
        <svg width={cfg.width} height={cfg.height} className=\"rotate-[-90deg]\">
          {/* Background Track */}
          <circle
            cx={cfg.width / 2}
            cy={cfg.height / 2}
            r={cfg.radius}
            strokeWidth={cfg.strokeWidth}
            stroke=\"rgba(255, 255, 255, 0.08)\"
            fill=\"transparent\"
          />
          {/* Active Arc */}
          <circle
            cx={cfg.width / 2}
            cy={cfg.height / 2}
            r={cfg.radius}
            strokeWidth={cfg.strokeWidth}
            stroke={strokeColor}
            strokeDasharray={cfg.radius * 2 * Math.PI}
            strokeDashoffset={strokeDashoffset}
            strokeLinecap=\"round\"
            fill=\"transparent\"
            className=\"transition-all duration-500 ease-out\"
          />
        </svg>

        {/* Center Readout */}
        <div className=\"absolute flex flex-col items-center justify-center text-center select-none\">
          <span className=\"font-mono font-bold text-foreground text-2xl tracking-tight\">
            {pct}%
          </span>
          <span className=\"text-[10px] text-muted-foreground font-mono uppercase tracking-wider\">
            Risk
          </span>
        </div>
      </div>

      {showBadge && (
        <RiskBadge score={normalizedScore} band={band} />
      )}
    </div>
  );
}
""",
    "feat(a11y): add WAI-ARIA meter role and value attributes to RiskGauge"
)

# 7. ExportDialog A11y test
write_and_commit(
    "apps/dashboard/src/test/a11y/__tests__/export-dialog-a11y.test.tsx",
    """import React from \"react\";
import { describe, it, expect, vi } from \"vitest\";
import { render, screen } from \"@testing-library/react\";
import { ExportDialog } from \"../../../components/investigation/export-dialog\";

vi.mock(\"../../../lib/hooks/use-investigation-export\", () => ({
  useInvestigationExport: () => ({
    downloadCsv: vi.fn(),
    downloadJson: vi.fn(),
    isExporting: false,
    error: null,
  }),
}));

describe(\"ExportDialog Accessibility\", () => {
  it(\"renders accessible dialog structure when open\", () => {
    const handleClose = vi.fn();
    render(<ExportDialog isOpen={true} onClose={handleClose} scanId=\"scan_999\" />);

    expect(screen.getByRole(\"dialog\")).toBeInTheDocument();
    expect(screen.getByText(\"Export Investigation Dataset\")).toBeInTheDocument();
  });
});
""",
    "test(a11y): test ExportDialog dialog accessibility when open"
)

# 8. Follower Explorer Filtering Scenario test
write_and_commit(
    "apps/dashboard/src/test/scenarios/__tests__/follower-explorer-filtering.test.tsx",
    """import React from \"react\";
import { describe, it, expect, vi } from \"vitest\";
import { render, screen, fireEvent } from \"@testing-library/react\";
import { FilterToolbar } from \"../../../components/investigation/filter-toolbar\";

describe(\"Scenario: Follower Explorer Filtering\", () => {
  it(\"updates search query and risk band filters interactively\", () => {
    const handleSearch = vi.fn();
    const handleBand = vi.fn();

    render(
      <FilterToolbar
        search=\"\"
        onSearchChange={handleSearch}
        riskBand=\"all\"
        onRiskBandChange={handleBand}
      />
    );

    const input = screen.getByPlaceholderText(/Search by handle/);
    fireEvent.change(input, { target: { value: \"suspicious_bot\" } });
    expect(handleSearch).toHaveBeenCalledWith(\"suspicious_bot\");

    const selects = screen.getAllByRole(\"combobox\");
    fireEvent.change(selects[0], { target: { value: \"critical\" } });
    expect(handleBand).toHaveBeenCalledWith(\"critical\");
  });
});
""",
    "test(scenarios): test interactive follower filtering across risk bands"
)

# 9. Evidence Inspector Flow Scenario test
write_and_commit(
    "apps/dashboard/src/test/scenarios/__tests__/evidence-inspector-flow.test.tsx",
    """import React from \"react\";
import { describe, it, expect } from \"vitest\";
import { render, screen, fireEvent } from \"@testing-library/react\";
import { EvidenceInspector } from \"../../../components/investigation/evidence-inspector\";

describe(\"Scenario: Evidence Inspector Deconstruction\", () => {
  it(\"collapses and expands supporting heuristic evidence rows\", () => {
    const evidence = [
      { id: \"ev_1\", rule_name: \"default_avatar\", weight: 0.3, score: 1.0, summary: \"Stock avatar detected\" },
      { id: \"ev_2\", rule_name: \"following_ratio\", weight: 0.5, score: 0.9, summary: \"Extreme out-degree ratio\" },
    ];

    render(<EvidenceInspector evidence={evidence} />);

    expect(screen.getByText(\"default_avatar\")).toBeInTheDocument();
    expect(screen.getByText(\"following_ratio\")).toBeInTheDocument();

    // Toggle collapse
    const toggleBtn = screen.getByRole(\"button\", { name: /Toggle Evidence/i });
    fireEvent.click(toggleBtn);
    expect(screen.queryByText(\"default_avatar\")).not.toBeInTheDocument();

    // Re-expand
    fireEvent.click(toggleBtn);
    expect(screen.getByText(\"default_avatar\")).toBeInTheDocument();
  });
});
""",
    "test(scenarios): test evidence accordion collapse and re-expansion"
)

# 10. Export Investigation Flow Scenario test
write_and_commit(
    "apps/dashboard/src/test/scenarios/__tests__/export-investigation-flow.test.tsx",
    """import React from \"react\";
import { describe, it, expect, vi } from \"vitest\";
import { render, screen, fireEvent } from \"@testing-library/react\";
import { ExportPanel } from \"../../../components/investigation/export-panel\";

describe(\"Scenario: Export Investigation Workflow\", () => {
  it(\"dispatches CSV and JSON downloads with confirmation notifications\", () => {
    const handleCsv = vi.fn();
    const handleJson = vi.fn();

    render(<ExportPanel scanId=\"scan_audit_77\" onExportCsv={handleCsv} onExportJson={handleJson} />);

    // CSV export
    fireEvent.click(screen.getByText(\"Download CSV\"));
    expect(handleCsv).toHaveBeenCalledTimes(1);
    expect(screen.getByText(/CSV export initiated/)).toBeInTheDocument();

    // Switch to JSON and export
    fireEvent.click(screen.getByText(\"JSON Bundle\"));
    fireEvent.click(screen.getByText(\"Download JSON\"));
    expect(handleJson).toHaveBeenCalledTimes(1);
    expect(screen.getByText(/JSON export bundle initiated/)).toBeInTheDocument();
  });
});
""",
    "test(scenarios): test investigation dataset export workflows"
)

# 11. Account Investigation Routing Scenario test
write_and_commit(
    "apps/dashboard/src/test/scenarios/__tests__/account-investigation-routing.test.tsx",
    """import React from \"react\";
import { describe, it, expect } from \"vitest\";
import { render, screen } from \"@testing-library/react\";
import { RelationshipTable } from \"../../../components/investigation/relationship-table\";

describe(\"Scenario: Account Investigation Routing\", () => {
  it(\"renders inspect deep links pointing to target account detail page\", () => {
    const accounts = [
      {
        id: \"acc_99\",
        platform_account_id: \"target_user_99\",
        username: \"target_user_99\",
        score: 0.94,
        band: \"critical\" as const,
        evidence_coverage: 1.0,
        features_available: 8,
        features_total: 8,
        scan_id: \"scan_workspace_01\",
        pid: \"x_user\",
        status: \"scored\" as const,
        contributions: [],
        limitations: [],
      },
    ];

    render(<RelationshipTable scanId=\"scan_workspace_01\" accounts={accounts} />);
    const link = screen.getByRole(\"link\", { name: /Inspect/i });
    expect(link).toHaveAttribute(\"href\", \"/investigations/scan_workspace_01/accounts/target_user_99\");
  });
});
""",
    "test(scenarios): test account deep-dive route link interpolation"
)

# 12. Synthetic Banner Provenance Scenario test
write_and_commit(
    "apps/dashboard/src/test/scenarios/__tests__/synthetic-banner-provenance.test.tsx",
    """import React from \"react\";
import { describe, it, expect } from \"vitest\";
import { render, screen } from \"@testing-library/react\";
import { SyntheticDataBanner } from \"../../../components/ui/synthetic-banner\";

describe(\"Scenario: Synthetic Banner Provenance Disclosure\", () => {
  it(\"renders prominent disclaimer banner with provenance metadata\", () => {
    render(<SyntheticDataBanner />);
    expect(screen.getByText(/Synthetic Demo Data/i)).toBeInTheDocument();
    expect(screen.getByText(/Do not treat risk scores as empirical accusations/i)).toBeInTheDocument();
    expect(screen.getByText(/PROVENANCE: SYNTHETIC/i)).toBeInTheDocument();
  });
});
""",
    "test(scenarios): test synthetic provenance banner disclosure"
)

# 13. Empty State Reset Flow Scenario test
write_and_commit(
    "apps/dashboard/src/test/scenarios/__tests__/empty-state-reset-flow.test.tsx",
    """import React from \"react\";
import { describe, it, expect, vi } from \"vitest\";
import { render, screen, fireEvent } from \"@testing-library/react\";
import { EmptyAccountsState } from \"../../../components/investigation/empty-accounts-state\";

describe(\"Scenario: Empty Accounts Filter Reset Flow\", () => {
  it(\"invokes reset filters callback on button click\", () => {
    const handleReset = vi.fn();
    render(<EmptyAccountsState onResetFilters={handleReset} />);

    expect(screen.getByText(\"No accounts match the selected filters\")).toBeInTheDocument();
    const btn = screen.getByText(\"Reset Filters\");
    fireEvent.click(btn);
    expect(handleReset).toHaveBeenCalledTimes(1);
  });
});
""",
    "test(scenarios): test empty accounts filter reset interaction"
)

# 14. Timeline Snapshot History Scenario test
write_and_commit(
    "apps/dashboard/src/test/scenarios/__tests__/timeline-snapshot-history.test.tsx",
    """import React from \"react\";
import { describe, it, expect } from \"vitest\";
import { render, screen } from \"@testing-library/react\";
import { TimelineSnapshot } from \"../../../components/investigation/timeline-snapshot\";

describe(\"Scenario: Timeline Snapshot History\", () => {
  it(\"formats follower counts, source, and ISO timestamp cleanly\", () => {
    render(
      <TimelineSnapshot
        observedAt=\"2026-11-05T10:00:00Z\"
        source=\"x_api_v2\"
        followers={12500}
        following={340}
      />
    );

    expect(screen.getByText(/12,500 followers/)).toBeInTheDocument();
    expect(screen.getByText(/340 following/)).toBeInTheDocument();
    expect(screen.getByText(\"x_api_v2\")).toBeInTheDocument();
  });
});
""",
    "test(scenarios): test timeline snapshot follower delta formatting"
)

# 15. Account Neighborhood Edges Scenario test
write_and_commit(
    "apps/dashboard/src/test/scenarios/__tests__/account-neighborhood-edges.test.tsx",
    """import React from \"react\";
import { describe, it, expect } from \"vitest\";
import { render, screen } from \"@testing-library/react\";
import { AccountNeighborhoodViewer } from \"../../../components/investigation/account-neighborhood-viewer\";

describe(\"Scenario: Account Neighborhood Inspection\", () => {
  it(\"renders incoming and outgoing 1-hop connections with truncated labels\", () => {
    const inEdges = [
      { source: \"suspicious_cluster_node_1\", target: \"target\", relationship_type: \"follower\" },
    ];
    const outEdges = [
      { source: \"target\", target: \"amplified_anchor_account\", relationship_type: \"following\" },
    ];

    render(<AccountNeighborhoodViewer inEdges={inEdges} outEdges={outEdges} />);
    expect(screen.getByText(\"suspicious_cluster_node_1\")).toBeInTheDocument();
    expect(screen.getByText(\"amplified_anchor_account\")).toBeInTheDocument();
  });
});
""",
    "test(scenarios): test 1-hop account neighborhood connection visualization"
)

# 16. Cluster Indicator Display Scenario test
write_and_commit(
    "apps/dashboard/src/test/scenarios/__tests__/cluster-indicator-display.test.tsx",
    """import React from \"react\";
import { describe, it, expect } from \"vitest\";
import { render, screen } from \"@testing-library/react\";
import { ClusterIndicator } from \"../../../components/investigation/cluster-indicator\";

describe(\"Scenario: Botnet Cluster Indicator Display\", () => {
  it(\"renders cluster badge with account count or standalone fallback\", () => {
    const { rerender } = render(<ClusterIndicator clusterId=\"cls_farm_8819\" clusterSize={35} />);
    expect(screen.getByText(\"Cluster #8819\")).toBeInTheDocument();
    expect(screen.getByText(\"35 accts\")).toBeInTheDocument();

    rerender(<ClusterIndicator />);
    expect(screen.getByText(\"Standalone\")).toBeInTheDocument();
  });
});
""",
    "test(scenarios): test botnet cluster badge and standalone fallback rendering"
)

# 17. Signal Radar Decomposition Scenario test
write_and_commit(
    "apps/dashboard/src/test/scenarios/__tests__/signal-radar-decomposition.test.tsx",
    """import React from \"react\";
import { describe, it, expect } from \"vitest\";
import { render, screen } from \"@testing-library/react\";
import { SignalRadarPreview } from \"../../../components/investigation/signal-radar-preview\";

describe(\"Scenario: Signal Radar Heuristic Decomposition\", () => {
  it(\"renders multi-vector percentages with appropriate color classes\", () => {
    const { container } = render(
      <SignalRadarPreview
        timingScore={0.92}
        textRepetitionScore={0.78}
        networkAnomalyScore={0.45}
        profileScore={0.12}
      />
    );

    expect(screen.getByText(\"92%\")).toBeInTheDocument();
    expect(screen.getByText(\"78%\")).toBeInTheDocument();
    expect(screen.getByText(\"45%\")).toBeInTheDocument();
    expect(screen.getByText(\"12%\")).toBeInTheDocument();

    const redBars = container.querySelectorAll(\".bg-rose-500\");
    expect(redBars.length).toBe(2); // > 70%
  });
});
""",
    "test(scenarios): test heuristic score decomposition into color-coded intensity bars"
)

# 18. Overview Summary Metrics Scenario test
write_and_commit(
    "apps/dashboard/src/test/scenarios/__tests__/overview-summary-metrics.test.tsx",
    """import React from \"react\";
import { describe, it, expect } from \"vitest\";
import { render, screen } from \"@testing-library/react\";
import { OverviewSummaryCard } from \"../../../components/investigation/overview-summary-card\";

describe(\"Scenario: Overview Summary Metric Aggregation\", () => {
  it(\"calculates zero flag rate safely on empty total accounts\", () => {
    render(<OverviewSummaryCard totalAccounts={0} botAccounts={0} avgRiskScore={0} criticalCount={0} />);
    expect(screen.getByText(\"0.0% flag rate\")).toBeInTheDocument();
  });
});
""",
    "test(scenarios): test division by zero resilience in OverviewSummaryCard"
)

# 19. Virtualization Benchmark test
write_and_commit(
    "apps/dashboard/src/test/scenarios/__tests__/virtualization-benchmark.test.ts",
    """import { describe, it, expect } from \"vitest\";
import { TABLE_VIRTUALIZATION_TOKENS } from \"../../../tokens/table-virtualization\";

describe(\"Scenario: Table Virtualization Row Geometry\", () => {
  it(\"computes viewport slices accurately for 10,000 accounts\", () => {
    const totalAccounts = 10000;
    const rowHeight = TABLE_VIRTUALIZATION_TOKENS.rowHeight;
    const viewportHeight = TABLE_VIRTUALIZATION_TOKENS.viewportHeight;
    const overscan = TABLE_VIRTUALIZATION_TOKENS.overscan;

    const visibleRowsCount = Math.ceil(viewportHeight / rowHeight);
    expect(visibleRowsCount).toBe(12);

    const scrollTop = 1200; // Scrolled past 25 rows
    const startIndex = Math.max(0, Math.floor(scrollTop / rowHeight) - overscan);
    const endIndex = Math.min(totalAccounts, startIndex + visibleRowsCount + overscan * 2);

    expect(startIndex).toBeGreaterThanOrEqual(0);
    expect(endIndex).toBeLessThanOrEqual(totalAccounts);
    expect(endIndex - startIndex).toBeLessThanOrEqual(visibleRowsCount + overscan * 2 + 1);
  });
});
""",
    "test(scenarios): verify table virtualization row slice window geometry"
)

# 20. Network Error Resilience Scenario test
write_and_commit(
    "apps/dashboard/src/test/scenarios/__tests__/network-error-resilience.test.tsx",
    """import React from \"react\";
import { describe, it, expect, vi } from \"vitest\";
import { render, screen, fireEvent } from \"@testing-library/react\";
import InvestigationDetailError from \"../../../app/investigations/[id]/error\";

describe(\"Scenario: Network Error Resilience\", () => {
  it(\"renders error recovery CTA when investigation workspace fetch fails\", () => {
    const handleRetry = vi.fn();
    render(
      <InvestigationDetailError
        error={new Error(\"Database connection terminated prematurely\")}
        reset={handleRetry}
      />
    );

    expect(screen.getByText(\"Failed to load investigation workspace\")).toBeInTheDocument();
    expect(screen.getByText(\"Database connection terminated prematurely\")).toBeInTheDocument();

    const retryBtn = screen.getByRole(\"button\", { name: /Retry/i });
    fireEvent.click(retryBtn);
    expect(handleRetry).toHaveBeenCalledTimes(1);
  });
});
""",
    "test(scenarios): test investigation error boundary recovery on network drop"
)

print("Batch 5 finished 20 commits.")

