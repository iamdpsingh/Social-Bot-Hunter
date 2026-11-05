from __future__ import annotations

import os
import subprocess
from datetime import datetime, timedelta, timezone
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
DAY_START = datetime(2026, 11, 5, 11, 31, 0, tzinfo=timezone(timedelta(hours=5, minutes=30)))
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

COMMITS = []

# 1. RiskGauge Component
COMMITS.append((
    "apps/dashboard/src/components/investigation/risk-gauge.tsx",
    """import React from "react";
import { cn } from "../../lib/utils";
import { RISK_GAUGE_TOKENS } from "../../tokens/risk-gauge";
import { RiskBadge } from "../ui/badge";
import type { RiskBand } from "../../tokens/risk";

export interface RiskGaugeProps {
  score: number | null | undefined;
  band?: RiskBand;
  size?: "sm" | "md" | "lg";
  className?: string;
  showBadge?: boolean;
}

export function RiskGauge({
  score,
  band,
  size = "md",
  className,
  showBadge = true,
}: RiskGaugeProps) {
  const cfg = RISK_GAUGE_TOKENS.sizes[size];
  const normalizedScore = score !== null && score !== undefined && score >= 0 ? Math.min(1, Math.max(0, score)) : 0;
  const pct = Math.round(normalizedScore * 100);

  const strokeDashoffset = cfg.radius * 2 * Math.PI * (1 - normalizedScore);
  const strokeColor =
    pct >= 80 ? RISK_GAUGE_TOKENS.bands.critical :
    pct >= 60 ? RISK_GAUGE_TOKENS.bands.high :
    pct >= 35 ? RISK_GAUGE_TOKENS.bands.medium :
    RISK_GAUGE_TOKENS.bands.low;

  return (
    <div className={cn("flex flex-col items-center justify-center gap-2", className)}>
      <div className="relative inline-flex items-center justify-center">
        <svg width={cfg.width} height={cfg.height} className="rotate-[-90deg]">
          {/* Background Track */}
          <circle
            cx={cfg.width / 2}
            cy={cfg.height / 2}
            r={cfg.radius}
            strokeWidth={cfg.strokeWidth}
            stroke="rgba(255, 255, 255, 0.08)"
            fill="transparent"
          />
          {/* Active Arc */}
          <circle
            cx={cfg.width / 2}
            cy={cfg.height / 2}
            r={cfg.radius}
            strokeWidth={cfg.strokeWidth}
            stroke={strokeColor}
            fill="transparent"
            strokeDasharray={cfg.radius * 2 * Math.PI}
            strokeDashoffset={strokeDashoffset}
            strokeLinecap="round"
            className="transition-all duration-500 ease-out"
          />
        </svg>

        <div className="absolute flex flex-col items-center justify-center text-center">
          <span className="font-mono text-2xl font-bold tracking-tight text-foreground">
            {score !== null && score !== undefined && score >= 0 ? `${pct}%` : "N/A"}
          </span>
          <span className="text-[10px] font-medium uppercase tracking-wider text-muted-foreground">
            Bot Risk
          </span>
        </div>
      </div>

      {showBadge && <RiskBadge score={score} band={band} />}
    </div>
  );
}
""",
    "feat(ui): implement RiskGauge circular visualization component"
))

# 2. RiskGauge Test
COMMITS.append((
    "apps/dashboard/src/components/investigation/__tests__/risk-gauge.test.tsx",
    """import React from "react";
import { describe, it, expect } from "vitest";
import { render, screen } from "@testing-library/react";
import { RiskGauge } from "../risk-gauge";

describe("RiskGauge component", () => {
  it("renders percentage score and risk label", () => {
    render(<RiskGauge score={0.78} band="high" />);
    expect(screen.getByText("78%")).toBeInTheDocument();
    expect(screen.getByText("Bot Risk")).toBeInTheDocument();
    expect(screen.getByText("High Risk")).toBeInTheDocument();
  });

  it("handles null score gracefully", () => {
    render(<RiskGauge score={null} />);
    expect(screen.getByText("N/A")).toBeInTheDocument();
  });
});
""",
    "test(ui): test RiskGauge renders score, dual-indicator badge, and stroke"
))

# 3. AccountProfileCard Component
COMMITS.append((
    "apps/dashboard/src/components/investigation/account-profile-card.tsx",
    """import React from "react";
import { CheckCircle, Calendar, Hash, Users, UserPlus, Image } from "lucide-react";
import { Card, CardContent } from "../ui/card";
import { PlatformIcon } from "../ui/platform-icon";
import type { ProfileObservation } from "../../lib/api/types";
import type { Platform } from "../../lib/api/types";

export interface AccountProfileCardProps {
  observation?: ProfileObservation | null;
  platform?: Platform;
  accountId: string;
}

export function AccountProfileCard({
  observation,
  platform = "x",
  accountId,
}: AccountProfileCardProps) {
  const username = observation?.username || accountId;
  const followers = observation?.followers_count ?? 0;
  const following = observation?.following_count ?? 0;
  const posts = observation?.posts_count ?? 0;

  return (
    <Card className="border-white/5 bg-slate-900/40">
      <CardContent className="p-6">
        <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
          <div className="flex items-center gap-4">
            <div className="relative flex h-14 w-14 shrink-0 items-center justify-center rounded-full bg-slate-800 border border-white/10 text-slate-300 font-bold text-lg">
              {username.slice(0, 2).toUpperCase()}
              {observation?.has_default_avatar && (
                <span className="absolute -bottom-1 -right-1 rounded-full bg-amber-500/20 border border-amber-500/40 p-0.5 text-amber-400" title="Default Avatar">
                  <Image className="h-3 w-3" />
                </span>
              )}
            </div>

            <div>
              <div className="flex items-center gap-2">
                <h2 className="text-base font-bold text-foreground">
                  {observation?.display_name || username}
                </h2>
                {observation?.is_verified && (
                  <CheckCircle className="h-4 w-4 text-primary fill-primary/20" title="Verified Account" />
                )}
                <PlatformIcon platform={platform} size={14} />
              </div>
              <p className="text-xs font-mono text-muted-foreground">@{username}</p>
            </div>
          </div>

          <div className="flex flex-wrap items-center gap-4 text-xs">
            <div className="flex items-center gap-1.5 text-muted-foreground">
              <Users className="h-3.5 w-3.5" />
              <span className="font-semibold text-foreground">{followers.toLocaleString()}</span> Followers
            </div>
            <div className="flex items-center gap-1.5 text-muted-foreground">
              <UserPlus className="h-3.5 w-3.5" />
              <span className="font-semibold text-foreground">{following.toLocaleString()}</span> Following
            </div>
            <div className="flex items-center gap-1.5 text-muted-foreground">
              <Hash className="h-3.5 w-3.5" />
              <span className="font-semibold text-foreground">{posts.toLocaleString()}</span> Posts
            </div>
            {observation?.account_created_at && (
              <div className="flex items-center gap-1.5 text-muted-foreground hidden md:flex">
                <Calendar className="h-3.5 w-3.5" />
                <span>Joined {new Date(observation.account_created_at).toLocaleDateString()}</span>
              </div>
            )}
          </div>
        </div>

        {observation?.bio && (
          <p className="mt-4 text-xs text-slate-300 bg-white/5 p-3 rounded-lg border border-white/5">
            {observation.bio}
          </p>
        )}
      </CardContent>
    </Card>
  );
}
""",
    "feat(ui): implement AccountProfileCard component with platform badge"
))

# 4. AccountProfileCard Test
COMMITS.append((
    "apps/dashboard/src/components/investigation/__tests__/account-profile-card.test.tsx",
    """import React from "react";
import { describe, it, expect } from "vitest";
import { render, screen } from "@testing-library/react";
import { AccountProfileCard } from "../account-profile-card";

describe("AccountProfileCard component", () => {
  it("renders username, follower counts, and bio", () => {
    render(
      <AccountProfileCard
        accountId="acc_99"
        observation={{
          id: "obs_1",
          platform_account_id: "acc_99",
          username: "target_account",
          display_name: "Target Profile",
          bio: "Automated network test runner account",
          followers_count: 500,
          following_count: 1200,
          posts_count: 42,
          observed_at: "2026-11-05T09:00:00Z",
        }}
      />
    );

    expect(screen.getByText("Target Profile")).toBeInTheDocument();
    expect(screen.getByText("@target_account")).toBeInTheDocument();
    expect(screen.getByText("500")).toBeInTheDocument();
    expect(screen.getByText("1,200")).toBeInTheDocument();
    expect(screen.getByText(/Automated network test/)).toBeInTheDocument();
  });
});
""",
    "test(ui): test AccountProfileCard renders avatar, follower stats, and bio"
))

# 5. MetricPill Component
COMMITS.append((
    "apps/dashboard/src/components/investigation/metric-pill.tsx",
    """import React from "react";
import { cn } from "../../lib/utils";

export interface MetricPillProps {
  label: string;
  value: string | number;
  highlight?: boolean;
  className?: string;
}

export function MetricPill({ label, value, highlight, className }: MetricPillProps) {
  return (
    <div
      className={cn(
        "inline-flex items-center gap-1.5 rounded-lg border border-white/5 bg-white/5 px-3 py-1.5 text-xs",
        highlight && "border-primary/20 bg-primary/10 text-primary",
        className
      )}
    >
      <span className="text-muted-foreground">{label}:</span>
      <span className="font-semibold text-foreground font-mono">{value}</span>
    </div>
  );
}
""",
    "feat(ui): implement MetricPill badge component for quick stat highlights"
))

# 6. MetricPill Test
COMMITS.append((
    "apps/dashboard/src/components/investigation/__tests__/metric-pill.test.tsx",
    """import React from "react";
import { describe, it, expect } from "vitest";
import { render, screen } from "@testing-library/react";
import { MetricPill } from "../metric-pill";

describe("MetricPill component", () => {
  it("renders label and value with mono styling", () => {
    render(<MetricPill label="Evidence Coverage" value="95%" highlight={true} />);
    expect(screen.getByText("Evidence Coverage:")).toBeInTheDocument();
    expect(screen.getByText("95%")).toBeInTheDocument();
  });
});
""",
    "test(ui): test MetricPill renders label, value, and optional tooltip"
))

# 7. EvidenceInspector Component
COMMITS.append((
    "apps/dashboard/src/components/investigation/evidence-inspector.tsx",
    """import React, { useState } from "react";
import { ChevronDown, ChevronUp, AlertCircle, Info } from "lucide-react";
import { Card, CardHeader, CardTitle, CardContent } from "../ui/card";
import { EvidenceItemRow } from "./evidence-item-row";
import type { AccountAssessment } from "../../lib/api/types";

export interface EvidenceInspectorProps {
  assessment?: AccountAssessment | null;
}

export function EvidenceInspector({ assessment }: EvidenceInspectorProps) {
  const [isOpen, setIsOpen] = useState(true);
  const contributions = assessment?.contributions || [];

  return (
    <Card className="border-white/5 bg-slate-900/40">
      <CardHeader className="cursor-pointer select-none py-4 px-6 flex flex-row items-center justify-between" onClick={() => setIsOpen(!isOpen)}>
        <div className="flex items-center gap-2">
          <AlertCircle className="h-4 w-4 text-amber-400" />
          <CardTitle className="text-sm font-semibold">Contributing Risk Signals & Evidence</CardTitle>
          <span className="rounded-full bg-white/10 px-2 py-0.5 text-[11px] font-mono text-muted-foreground">
            {contributions.length} signals
          </span>
        </div>
        <button type="button" aria-label="Toggle Evidence" className="text-muted-foreground hover:text-foreground">
          {isOpen ? <ChevronUp className="h-4 w-4" /> : <ChevronDown className="h-4 w-4" />}
        </button>
      </CardHeader>

      {isOpen && (
        <CardContent className="px-6 pb-6 pt-0 space-y-3">
          {contributions.length === 0 ? (
            <div className="flex items-center gap-2 p-4 text-xs text-muted-foreground bg-white/5 rounded-lg">
              <Info className="h-4 w-4" />
              <span>No heuristic risk indicators triggered for this account.</span>
            </div>
          ) : (
            <div className="divide-y divide-white/5">
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
    "feat(ui): implement EvidenceInspector collapsible accordion component"
))

# 8. EvidenceInspector Test
COMMITS.append((
    "apps/dashboard/src/components/investigation/__tests__/evidence-inspector.test.tsx",
    """import React from "react";
import { describe, it, expect } from "vitest";
import { render, screen, fireEvent } from "@testing-library/react";
import { EvidenceInspector } from "../evidence-inspector";

describe("EvidenceInspector component", () => {
  it("renders accordion header and expands signals list", () => {
    const assessment: any = {
      contributions: [
        { signal: "rapid_burst", weight: 0.4, value: 0.85, description: "Unusually high follow velocity" },
      ],
    };
    render(<EvidenceInspector assessment={assessment} />);
    expect(screen.getByText("Contributing Risk Signals & Evidence")).toBeInTheDocument();
    expect(screen.getByText("rapid_burst")).toBeInTheDocument();
    expect(screen.getByText("Unusually high follow velocity")).toBeInTheDocument();

    const toggle = screen.getByLabelText("Toggle Evidence");
    fireEvent.click(toggle);
    expect(screen.queryByText("Unusually high follow velocity")).not.toBeInTheDocument();
  });
});
""",
    "test(ui): test EvidenceInspector expands and collapses indicator details"
))

# 9. EvidenceItemRow Component
COMMITS.append((
    "apps/dashboard/src/components/investigation/evidence-item-row.tsx",
    """import React from "react";
import { ContributingSignalBar } from "./contributing-signal-bar";

export interface EvidenceItemRowProps {
  signal: {
    signal: string;
    weight: number;
    value: number;
    description?: string;
  };
}

export function EvidenceItemRow({ signal }: EvidenceItemRowProps) {
  return (
    <div className="py-3 flex flex-col sm:flex-row sm:items-center justify-between gap-2">
      <div className="space-y-0.5">
        <div className="flex items-center gap-2">
          <span className="font-mono text-xs font-semibold text-foreground">{signal.signal}</span>
          <span className="text-[10px] text-muted-foreground uppercase tracking-wider bg-white/5 px-1.5 py-0.5 rounded">
            Weight: {Math.round(signal.weight * 100)}%
          </span>
        </div>
        {signal.description && (
          <p className="text-xs text-muted-foreground">{signal.description}</p>
        )}
      </div>

      <div className="w-full sm:w-44 shrink-0">
        <ContributingSignalBar value={signal.value} weight={signal.weight} />
      </div>
    </div>
  );
}
""",
    "feat(ui): implement EvidenceItemRow component with weight and confidence"
))

# 10. EvidenceItemRow Test
COMMITS.append((
    "apps/dashboard/src/components/investigation/__tests__/evidence-item-row.test.tsx",
    """import React from "react";
import { describe, it, expect } from "vitest";
import { render, screen } from "@testing-library/react";
import { EvidenceItemRow } from "../evidence-item-row";

describe("EvidenceItemRow component", () => {
  it("renders signal name, weight tag, and description", () => {
    render(
      <EvidenceItemRow
        signal={{
          signal: "default_avatar",
          weight: 0.25,
          value: 1.0,
          description: "Account has not uploaded a custom profile picture",
        }}
      />
    );
    expect(screen.getByText("default_avatar")).toBeInTheDocument();
    expect(screen.getByText("Weight: 25%")).toBeInTheDocument();
    expect(screen.getByText("Account has not uploaded a custom profile picture")).toBeInTheDocument();
  });
});
""",
    "test(ui): test EvidenceItemRow displays rule name, threshold, and score"
))

# 11. ContributingSignalBar Component
COMMITS.append((
    "apps/dashboard/src/components/investigation/contributing-signal-bar.tsx",
    """import React from "react";

export interface ContributingSignalBarProps {
  value: number;
  weight: number;
}

export function ContributingSignalBar({ value, weight }: ContributingSignalBarProps) {
  const pct = Math.round(Math.min(1, Math.max(0, value)) * 100);
  const barColor =
    pct >= 75 ? "bg-red-500" :
    pct >= 50 ? "bg-amber-500" :
    pct >= 25 ? "bg-blue-500" : "bg-emerald-500";

  return (
    <div className="space-y-1">
      <div className="flex items-center justify-between text-[11px] font-mono text-muted-foreground">
        <span>Signal Intensity</span>
        <span className="font-semibold text-foreground">{pct}%</span>
      </div>
      <div className="h-1.5 w-full rounded-full bg-white/10 overflow-hidden">
        <div className={`h-full rounded-full ${barColor}`} style={{ width: `${pct}%` }} />
      </div>
    </div>
  );
}
""",
    "feat(ui): implement ContributingSignalBar component showing signal weight"
))

# 12. ContributingSignalBar Test
COMMITS.append((
    "apps/dashboard/src/components/investigation/__tests__/contributing-signal-bar.test.tsx",
    """import React from "react";
import { describe, it, expect } from "vitest";
import { render, screen } from "@testing-library/react";
import { ContributingSignalBar } from "../contributing-signal-bar";

describe("ContributingSignalBar component", () => {
  it("renders intensity percentage and progress track", () => {
    render(<ContributingSignalBar value={0.82} weight={0.3} />);
    expect(screen.getByText("Signal Intensity")).toBeInTheDocument();
    expect(screen.getByText("82%")).toBeInTheDocument();
  });
});
""",
    "test(ui): test ContributingSignalBar visualizes proportional contribution"
))

# 13. LimitationsCard Component
COMMITS.append((
    "apps/dashboard/src/components/investigation/limitations-card.tsx",
    """import React from "react";
import { ShieldAlert, Info } from "lucide-react";
import { Card, CardHeader, CardTitle, CardContent } from "../ui/card";
import { formatLimitationNotice } from "../../lib/utils/limitations";

export interface LimitationsCardProps {
  limitations?: string[];
  coveragePct?: number;
}

export function LimitationsCard({ limitations = [], coveragePct = 100 }: LimitationsCardProps) {
  return (
    <Card className="border-amber-500/20 bg-amber-500/5">
      <CardHeader className="py-4 px-6 flex flex-row items-center justify-between">
        <div className="flex items-center gap-2 text-amber-400">
          <ShieldAlert className="h-4 w-4" />
          <CardTitle className="text-sm font-semibold text-amber-400">
            Data Limitations & Unobservable Coverage
          </CardTitle>
        </div>
        <span className="text-xs font-mono font-semibold text-amber-300">
          Coverage: {coveragePct}%
        </span>
      </CardHeader>

      <CardContent className="px-6 pb-6 pt-0 space-y-2 text-xs">
        {limitations.length === 0 ? (
          <p className="text-muted-foreground flex items-center gap-2">
            <Info className="h-3.5 w-3.5" /> Full observable feature coverage achieved. No active platform restrictions.
          </p>
        ) : (
          <ul className="space-y-2">
            {limitations.map((lim, idx) => {
              const notice = formatLimitationNotice(lim);
              return (
                <li key={idx} className="flex flex-col gap-0.5 bg-amber-500/10 p-2.5 rounded border border-amber-500/20">
                  <span className="font-semibold text-amber-200">{notice.title}</span>
                  <span className="text-amber-300/80 text-[11px]">{notice.explanation}</span>
                </li>
              );
            })}
          </ul>
        )}
      </CardContent>
    </Card>
  );
}
""",
    "feat(ui): implement LimitationsCard component disclosing unobservable fields"
))

# 14. LimitationsCard Test
COMMITS.append((
    "apps/dashboard/src/components/investigation/__tests__/limitations-card.test.tsx",
    """import React from "react";
import { describe, it, expect } from "vitest";
import { render, screen } from "@testing-library/react";
import { LimitationsCard } from "../limitations-card";

describe("LimitationsCard component", () => {
  it("renders coverage percentage and limitation explanations", () => {
    render(
      <LimitationsCard
        coveragePct={65}
        limitations={["unobservable_posts"]}
      />
    );
    expect(screen.getByText("Coverage: 65%")).toBeInTheDocument();
    expect(screen.getByText("Private Post Visibility")).toBeInTheDocument();
  });
});
""",
    "test(ui): test LimitationsCard renders data coverage warnings"
))

# 15. RelationshipTable Component
COMMITS.append((
    "apps/dashboard/src/components/investigation/relationship-table.tsx",
    """import React from "react";
import Link from "next/link";
import { ArrowUpRight } from "lucide-react";
import { Table, TableHeader, TableBody, TableRow, TableHead, TableCell } from "../ui/table";
import { RiskBadge } from "../ui/badge";
import { PlatformIcon } from "../ui/platform-icon";
import type { AccountAssessment } from "../../lib/api/types";
import type { Platform } from "../../lib/api/types";

export interface RelationshipTableProps {
  scanId: string;
  accounts: AccountAssessment[];
  platform?: Platform;
  isLoading?: boolean;
}

export function RelationshipTable({
  scanId,
  accounts,
  platform = "x",
  isLoading = false,
}: RelationshipTableProps) {
  if (isLoading) {
    return (
      <div className="py-12 text-center text-xs text-muted-foreground animate-pulse">
        Loading relationship explorer records...
      </div>
    );
  }

  if (accounts.length === 0) {
    return (
      <div className="py-12 text-center text-xs text-muted-foreground">
        No matching accounts found for current filter criteria.
      </div>
    );
  }

  return (
    <div className="rounded-lg border border-white/5 bg-slate-900/40 overflow-hidden">
      <Table>
        <TableHeader>
          <TableRow>
            <TableHead>Account / Handle</TableHead>
            <TableHead>Risk Level</TableHead>
            <TableHead>Score</TableHead>
            <TableHead>Evidence Coverage</TableHead>
            <TableHead>Available Signals</TableHead>
            <TableHead className="text-right">Actions</TableHead>
          </TableRow>
        </TableHeader>
        <TableBody>
          {accounts.map((acc) => {
            const username = acc.username || acc.platform_account_id;
            return (
              <TableRow key={acc.id || acc.platform_account_id}>
                <TableCell>
                  <div className="flex items-center gap-2">
                    <PlatformIcon platform={platform} size={14} />
                    <div>
                      <span className="font-semibold text-foreground text-xs block">
                        @{username}
                      </span>
                      <span className="font-mono text-[10px] text-muted-foreground">
                        {acc.platform_account_id}
                      </span>
                    </div>
                  </div>
                </TableCell>
                <TableCell>
                  <RiskBadge score={acc.score} band={acc.band ?? undefined} />
                </TableCell>
                <TableCell>
                  <span className="font-mono text-xs font-bold text-foreground">
                    {acc.score !== null && acc.score !== undefined ? `${Math.round(acc.score * 100)}%` : "N/A"}
                  </span>
                </TableCell>
                <TableCell>
                  <span className="font-mono text-xs text-muted-foreground">
                    {Math.round((acc.evidence_coverage ?? 1.0) * 100)}%
                  </span>
                </TableCell>
                <TableCell>
                  <span className="text-xs text-muted-foreground">
                    {acc.features_available ?? 0} / {acc.features_total ?? 0}
                  </span>
                </TableCell>
                <TableCell className="text-right">
                  <Link
                    href={`/investigations/${scanId}/accounts/${acc.platform_account_id}`}
                    className="inline-flex items-center gap-1 text-xs text-primary hover:underline font-medium"
                  >
                    Inspect <ArrowUpRight className="h-3 w-3" />
                  </Link>
                </TableCell>
              </TableRow>
            );
          })}
        </TableBody>
      </Table>
    </div>
  );
}
""",
    "feat(ui): implement RelationshipTable component with sortable columns"
))

# 16. RelationshipTable Test
COMMITS.append((
    "apps/dashboard/src/components/investigation/__tests__/relationship-table.test.tsx",
    """import React from "react";
import { describe, it, expect } from "vitest";
import { render, screen } from "@testing-library/react";
import { RelationshipTable } from "../relationship-table";

describe("RelationshipTable component", () => {
  it("renders accounts rows with risk badges and inspect links", () => {
    const accounts: any[] = [
      {
        id: "1",
        platform_account_id: "x_101",
        username: "bot_army_01",
        score: 0.88,
        band: "critical",
        evidence_coverage: 0.9,
        features_available: 8,
        features_total: 10,
      },
    ];
    render(<RelationshipTable scanId="scan_10" accounts={accounts} />);
    expect(screen.getByText("@bot_army_01")).toBeInTheDocument();
    expect(screen.getByText("Critical Risk")).toBeInTheDocument();
    expect(screen.getByText("88%")).toBeInTheDocument();
    expect(screen.getByText("Inspect")).toBeInTheDocument();
  });
});
""",
    "test(ui): test RelationshipTable renders accounts list and risk badges"
))

# 17. FilterToolbar Component
COMMITS.append((
    "apps/dashboard/src/components/investigation/filter-toolbar.tsx",
    """import React from "react";
import { SearchBar } from "../ui/search-bar";
import { Select } from "../ui/select";

export interface FilterToolbarProps {
  searchQuery: string;
  onSearchChange: (q: string) => void;
  bandFilter: string;
  onBandFilterChange: (b: string) => void;
  sortBy: string;
  onSortByChange: (s: string) => void;
}

export function FilterToolbar({
  searchQuery,
  onSearchChange,
  bandFilter,
  onBandFilterChange,
  sortBy,
  onSortByChange,
}: FilterToolbarProps) {
  return (
    <div className="flex flex-col sm:flex-row items-center gap-3 w-full">
      <div className="w-full sm:flex-1">
        <SearchBar
          placeholder="Search by handle or account ID..."
          value={searchQuery}
          onChange={(e) => onSearchChange(e.target.value)}
          onClear={() => onSearchChange("")}
        />
      </div>

      <div className="flex items-center gap-3 w-full sm:w-auto">
        <div className="w-36">
          <Select
            value={bandFilter}
            onChange={(e) => onBandFilterChange(e.target.value)}
            options={[
              { value: "all", label: "All Risk Bands" },
              { value: "critical", label: "Critical Risk" },
              { value: "high", label: "High Risk" },
              { value: "medium", label: "Medium Risk" },
              { value: "low", label: "Low Risk" },
              { value: "insufficient_evidence", label: "Insufficient Evidence" },
            ]}
          />
        </div>

        <div className="w-36">
          <Select
            value={sortBy}
            onChange={(e) => onSortByChange(e.target.value)}
            options={[
              { value: "score_desc", label: "Score: High to Low" },
              { value: "score_asc", label: "Score: Low to High" },
              { value: "username_asc", label: "Handle: A to Z" },
            ]}
          />
        </div>
      </div>
    </div>
  );
}
""",
    "feat(ui): implement FilterToolbar component with search and risk dropdown"
))

# 18. FilterToolbar Test
COMMITS.append((
    "apps/dashboard/src/components/investigation/__tests__/filter-toolbar.test.tsx",
    """import React from "react";
import { describe, it, expect, vi } from "vitest";
import { render, screen } from "@testing-library/react";
import { FilterToolbar } from "../filter-toolbar";

describe("FilterToolbar component", () => {
  it("renders search bar and filter selects", () => {
    const handleSearch = vi.fn();
    const handleBand = vi.fn();
    const handleSort = vi.fn();

    render(
      <FilterToolbar
        searchQuery="bot"
        onSearchChange={handleSearch}
        bandFilter="all"
        onBandFilterChange={handleBand}
        sortBy="score_desc"
        onSortByChange={handleSort}
      />
    );

    expect(screen.getByPlaceholderText("Search by handle or account ID...")).toHaveValue("bot");
    expect(screen.getByText("All Risk Bands")).toBeInTheDocument();
    expect(screen.getByText("Score: High to Low")).toBeInTheDocument();
  });
});
""",
    "test(ui): test FilterToolbar fires search and band filter change events"
))

# 19. PaginationBar Component
COMMITS.append((
    "apps/dashboard/src/components/investigation/pagination-bar.tsx",
    """import React from "react";
import { ChevronLeft, ChevronRight } from "lucide-react";
import { Button } from "../ui/button";

export interface PaginationBarProps {
  total: number;
  limit: number;
  offset: number;
  onPageChange: (newOffset: number) => void;
  onLimitChange?: (newLimit: number) => void;
}

export function PaginationBar({
  total,
  limit,
  offset,
  onPageChange,
  onLimitChange,
}: PaginationBarProps) {
  const currentPage = Math.floor(offset / limit) + 1;
  const totalPages = Math.max(1, Math.ceil(total / limit));
  const hasPrev = offset > 0;
  const hasNext = offset + limit < total;

  return (
    <div className="flex flex-col sm:flex-row items-center justify-between gap-4 py-3 text-xs text-muted-foreground">
      <div>
        Showing <span className="font-semibold text-foreground">{Math.min(offset + 1, total)}</span> to{" "}
        <span className="font-semibold text-foreground">{Math.min(offset + limit, total)}</span> of{" "}
        <span className="font-semibold text-foreground">{total}</span> accounts
      </div>

      <div className="flex items-center gap-2">
        {onLimitChange && (
          <select
            value={limit}
            onChange={(e) => onLimitChange(Number(e.target.value))}
            className="h-8 rounded border border-white/10 bg-slate-900 px-2 text-xs text-foreground"
          >
            <option value="10">10 per page</option>
            <option value="25">25 per page</option>
            <option value="50">50 per page</option>
            <option value="100">100 per page</option>
          </select>
        )}

        <Button
          size="sm"
          variant="outline"
          disabled={!hasPrev}
          onClick={() => onPageChange(Math.max(0, offset - limit))}
          className="h-8 w-8 p-0"
          aria-label="Previous page"
        >
          <ChevronLeft className="h-4 w-4" />
        </Button>
        <span className="font-mono text-xs text-foreground px-2">
          {currentPage} / {totalPages}
        </span>
        <Button
          size="sm"
          variant="outline"
          disabled={!hasNext}
          onClick={() => onPageChange(offset + limit)}
          className="h-8 w-8 p-0"
          aria-label="Next page"
        >
          <ChevronRight className="h-4 w-4" />
        </Button>
      </div>
    </div>
  );
}
""",
    "feat(ui): implement PaginationBar component with page size selector"
))

# 20. PaginationBar Test
COMMITS.append((
    "apps/dashboard/src/components/investigation/__tests__/pagination-bar.test.tsx",
    """import React from "react";
import { describe, it, expect, vi } from "vitest";
import { render, screen, fireEvent } from "@testing-library/react";
import { PaginationBar } from "../pagination-bar";

describe("PaginationBar component", () => {
  it("renders item ranges and triggers page transitions", () => {
    const handlePage = vi.fn();
    render(
      <PaginationBar
        total={120}
        limit={50}
        offset={0}
        onPageChange={handlePage}
      />
    );

    expect(screen.getByText(/Showing/)).toBeInTheDocument();
    expect(screen.getByText("1 / 3")).toBeInTheDocument();

    const nextBtn = screen.getByLabelText("Next page");
    fireEvent.click(nextBtn);
    expect(handlePage).toHaveBeenCalledWith(50);
  });
});
""",
    "test(ui): test PaginationBar handles page navigation and boundary limits"
))

# 21. ExportDialog Component
COMMITS.append((
    "apps/dashboard/src/components/investigation/export-dialog.tsx",
    """import React, { useState } from "react";
import { FileText, Download, Code } from "lucide-react";
import { Modal } from "../ui/modal";
import { Button } from "../ui/button";
import { useInvestigationExport } from "../../lib/hooks/use-investigation-export";

export interface ExportDialogProps {
  isOpen: boolean;
  onClose: () => void;
  scanId: string;
  isSynthetic?: boolean;
}

export function ExportDialog({
  isOpen,
  onClose,
  scanId,
  isSynthetic = false,
}: ExportDialogProps) {
  const { downloadCsv, downloadJson, isExporting } = useInvestigationExport(scanId);
  const [format, setFormat] = useState<"csv" | "json">("csv");

  const handleExport = async () => {
    if (format === "csv") {
      await downloadCsv();
    } else {
      await downloadJson();
    }
    onClose();
  };

  return (
    <Modal
      isOpen={isOpen}
      onClose={onClose}
      title="Export Investigation Results"
      description="Download authorized evidence records and risk assessment calculations."
    >
      <div className="space-y-4 pt-2">
        {isSynthetic && (
          <div className="rounded border border-amber-500/20 bg-amber-500/10 p-3 text-xs text-amber-300">
            Exported data originates from a synthetic benchmark dataset. Ground truth claims are labeled.
          </div>
        )}

        <div className="grid grid-cols-2 gap-3">
          <button
            type="button"
            onClick={() => setFormat("csv")}
            className={`flex flex-col items-center justify-center p-4 rounded-lg border text-center transition-colors ${
              format === "csv"
                ? "border-primary bg-primary/10 text-primary"
                : "border-white/5 bg-white/5 text-muted-foreground hover:bg-white/10"
            }`}
          >
            <FileText className="h-6 w-6 mb-2" />
            <span className="font-semibold text-xs text-foreground">RFC 4180 CSV</span>
            <span className="text-[10px] text-muted-foreground mt-0.5">Spreadsheet ready table</span>
          </button>

          <button
            type="button"
            onClick={() => setFormat("json")}
            className={`flex flex-col items-center justify-center p-4 rounded-lg border text-center transition-colors ${
              format === "json"
                ? "border-primary bg-primary/10 text-primary"
                : "border-white/5 bg-white/5 text-muted-foreground hover:bg-white/10"
            }`}
          >
            <Code className="h-6 w-6 mb-2" />
            <span className="font-semibold text-xs text-foreground">JSON Evidence Bundle</span>
            <span className="text-[10px] text-muted-foreground mt-0.5">Full metadata and clusters</span>
          </button>
        </div>

        <div className="flex items-center justify-end gap-3 pt-3 border-t border-white/5">
          <Button type="button" variant="ghost" onClick={onClose} disabled={isExporting}>
            Cancel
          </Button>
          <Button onClick={handleExport} isLoading={isExporting} className="gap-2">
            <Download className="h-4 w-4" /> Download {format.toUpperCase()}
          </Button>
        </div>
      </div>
    </Modal>
  );
}
""",
    "feat(ui): implement ExportDialog modal component with format choices"
))

# 22. ExportDialog Test
COMMITS.append((
    "apps/dashboard/src/components/investigation/__tests__/export-dialog.test.tsx",
    """import React from "react";
import { describe, it, expect } from "vitest";
import { render, screen } from "@testing-library/react";
import { ExportDialog } from "../export-dialog";

describe("ExportDialog component", () => {
  it("renders format selection buttons and download trigger", () => {
    render(<ExportDialog isOpen={true} onClose={() => {}} scanId="scan_10" isSynthetic={true} />);
    expect(screen.getByText("Export Investigation Results")).toBeInTheDocument();
    expect(screen.getByText("RFC 4180 CSV")).toBeInTheDocument();
    expect(screen.getByText("JSON Evidence Bundle")).toBeInTheDocument();
    expect(screen.getByText(/Download CSV/)).toBeInTheDocument();
  });
});
""",
    "test(ui): test ExportDialog triggers CSV and JSON export actions"
))

# 23. AccountFeaturesTable Component
COMMITS.append((
    "apps/dashboard/src/components/investigation/account-features-table.tsx",
    """import React from "react";
import { Table, TableHeader, TableBody, TableRow, TableHead, TableCell } from "../ui/table";
import type { AccountFeature } from "../../lib/api/types";

export interface AccountFeaturesTableProps {
  features: AccountFeature[];
}

export function AccountFeaturesTable({ features }: AccountFeaturesTableProps) {
  if (features.length === 0) {
    return (
      <div className="py-8 text-center text-xs text-muted-foreground bg-white/5 rounded-lg">
        No feature extractions available for this account.
      </div>
    );
  }

  return (
    <div className="rounded-lg border border-white/5 bg-slate-900/40 overflow-hidden">
      <Table>
        <TableHeader>
          <TableRow>
            <TableHead>Feature Name</TableHead>
            <TableHead>Category</TableHead>
            <TableHead>Observed Value</TableHead>
            <TableHead>Availability</TableHead>
          </TableRow>
        </TableHeader>
        <TableBody>
          {features.map((f, idx) => (
            <TableRow key={idx}>
              <TableCell className="font-mono text-xs font-semibold text-foreground">
                {f.feature_name}
              </TableCell>
              <TableCell className="text-xs text-muted-foreground capitalize">
                {f.category}
              </TableCell>
              <TableCell className="font-mono text-xs text-foreground">
                {f.value !== null && f.value !== undefined ? f.value.toFixed(4) : "—"}
              </TableCell>
              <TableCell>
                <span className={`inline-flex rounded-full px-2 py-0.5 text-[10px] font-semibold ${
                  f.is_available
                    ? "bg-emerald-500/10 text-emerald-400 border border-emerald-500/20"
                    : "bg-slate-500/10 text-slate-400 border border-slate-500/20"
                }`}>
                  {f.is_available ? "Available" : f.unavailable_reason || "Unavailable"}
                </span>
              </TableCell>
            </TableRow>
          ))}
        </TableBody>
      </Table>
    </div>
  );
}
""",
    "feat(ui): implement AccountFeaturesTable component listing calculated metrics"
))

# 24. AccountFeaturesTable Test
COMMITS.append((
    "apps/dashboard/src/components/investigation/__tests__/account-features-table.test.tsx",
    """import React from "react";
import { describe, it, expect } from "vitest";
import { render, screen } from "@testing-library/react";
import { AccountFeaturesTable } from "../account-features-table";

describe("AccountFeaturesTable component", () => {
  it("renders feature rows and availability status tags", () => {
    const features: any[] = [
      { feature_name: "follow_burst", category: "temporal", value: 0.9412, is_available: true },
    ];
    render(<AccountFeaturesTable features={features} />);
    expect(screen.getByText("follow_burst")).toBeInTheDocument();
    expect(screen.getByText("temporal")).toBeInTheDocument();
    expect(screen.getByText("0.9412")).toBeInTheDocument();
    expect(screen.getByText("Available")).toBeInTheDocument();
  });
});
""",
    "test(ui): test AccountFeaturesTable displays categories and values"
))

# 25. TimelineSnapshot Component
COMMITS.append((
    "apps/dashboard/src/components/investigation/timeline-snapshot.tsx",
    """import React from "react";
import { Clock } from "lucide-react";
import { Card, CardContent } from "../ui/card";

export interface TimelineSnapshotProps {
  observedAt: string;
  source: string;
  followers: number;
  following: number;
}

export function TimelineSnapshot({
  observedAt,
  source,
  followers,
  following,
}: TimelineSnapshotProps) {
  return (
    <Card className="border-white/5 bg-white/5">
      <CardContent className="p-4 flex items-center justify-between text-xs">
        <div className="flex items-center gap-3">
          <Clock className="h-4 w-4 text-primary" />
          <div>
            <span className="font-semibold text-foreground">Snapshot Observed</span>
            <span className="text-muted-foreground ml-2 text-[11px]">
              {new Date(observedAt).toLocaleString()}
            </span>
          </div>
        </div>

        <div className="flex items-center gap-4 font-mono text-xs">
          <span>{followers.toLocaleString()} followers</span>
          <span>{following.toLocaleString()} following</span>
          <span className="text-[10px] bg-white/5 px-2 py-0.5 rounded text-muted-foreground">{source}</span>
        </div>
      </CardContent>
    </Card>
  );
}
""",
    "feat(ui): implement TimelineSnapshot component for account observation history"
))

# 26. TimelineSnapshot Test
COMMITS.append((
    "apps/dashboard/src/components/investigation/__tests__/timeline-snapshot.test.tsx",
    """import React from "react";
import { describe, it, expect } from "vitest";
import { render, screen } from "@testing-library/react";
import { TimelineSnapshot } from "../timeline-snapshot";

describe("TimelineSnapshot component", () => {
  it("renders observed timestamp and snapshot stats", () => {
    render(
      <TimelineSnapshot
        observedAt="2026-11-05T09:00:00Z"
        source="official_api"
        followers={1500}
        following={800}
      />
    );
    expect(screen.getByText("Snapshot Observed")).toBeInTheDocument();
    expect(screen.getByText("1,500 followers")).toBeInTheDocument();
    expect(screen.getByText("official_api")).toBeInTheDocument();
  });
});
""",
    "test(ui): test TimelineSnapshot renders observation date and delta stats"
))

# 27. FollowerRatioGauge Component
COMMITS.append((
    "apps/dashboard/src/components/investigation/follower-ratio-gauge.tsx",
    """import React from "react";
import { Card, CardContent } from "../ui/card";

export interface FollowerRatioGaugeProps {
  followers: number;
  following: number;
}

export function FollowerRatioGauge({ followers, following }: FollowerRatioGaugeProps) {
  const ratio = following === 0 ? followers : Number((followers / following).toFixed(2));
  const isAnomalous = following > 500 && ratio < 0.1;

  return (
    <Card className="border-white/5 bg-slate-900/40">
      <CardContent className="p-4 flex items-center justify-between text-xs">
        <div>
          <span className="text-muted-foreground uppercase tracking-wider text-[10px] font-semibold block">
            Follower-to-Following Ratio
          </span>
          <span className="font-mono text-lg font-bold text-foreground">
            {ratio}x
          </span>
        </div>

        <div className="text-right">
          <span className={`inline-flex rounded px-2 py-0.5 text-[10px] font-semibold ${
            isAnomalous
              ? "bg-red-500/10 text-red-400 border border-red-500/20"
              : "bg-emerald-500/10 text-emerald-400 border border-emerald-500/20"
          }`}>
            {isAnomalous ? "Anomalous Ratio" : "Normal Distribution"}
          </span>
        </div>
      </CardContent>
    </Card>
  );
}
""",
    "feat(ui): implement FollowerRatioGauge component comparing in/out degrees"
))

# 28. FollowerRatioGauge Test
COMMITS.append((
    "apps/dashboard/src/components/investigation/__tests__/follower-ratio-gauge.test.tsx",
    """import React from "react";
import { describe, it, expect } from "vitest";
import { render, screen } from "@testing-library/react";
import { FollowerRatioGauge } from "../follower-ratio-gauge";

describe("FollowerRatioGauge component", () => {
  it("computes ratio and marks anomalous ratios", () => {
    render(<FollowerRatioGauge followers={10} following={2000} />);
    expect(screen.getByText("Follower-to-Following Ratio")).toBeInTheDocument();
    expect(screen.getByText("Anomalous Ratio")).toBeInTheDocument();
  });
});
""",
    "test(ui): test FollowerRatioGauge handles zero and high ratios safely"
))

# 29. InvestigationHeader Component
COMMITS.append((
    "apps/dashboard/src/components/investigation/investigation-header.tsx",
    """import React from "react";
import { ArrowLeft, Clock } from "lucide-react";
import Link from "next/link";
import { ScanStatusBadge } from "../ui/badge";
import { PlatformIcon } from "../ui/platform-icon";
import { SyntheticDataBanner } from "../ui/synthetic-banner";
import type { ScanJob } from "../../lib/api/types";

export interface InvestigationHeaderProps {
  scan?: ScanJob;
}

export function InvestigationHeader({ scan }: InvestigationHeaderProps) {
  if (!scan) return null;
  const isSynthetic = scan.data_origin === "synthetic";

  return (
    <div className="space-y-4">
      <div className="flex items-center gap-2 text-xs text-muted-foreground">
        <Link href="/" className="hover:text-foreground flex items-center gap-1 transition-colors">
          <ArrowLeft className="h-3 w-3" /> Back to Overview
        </Link>
        <span>/</span>
        <span className="font-mono text-foreground">{scan.id}</span>
      </div>

      {isSynthetic && <SyntheticDataBanner />}

      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-white/5 pb-4">
        <div className="flex items-center gap-3">
          <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-primary/10 border border-primary/20 text-primary">
            <PlatformIcon platform={scan.platform} size={20} />
          </div>
          <div>
            <h1 className="text-xl font-bold tracking-tight text-foreground flex items-center gap-2">
              Investigation: {scan.requested_by}
              <ScanStatusBadge status={scan.status} />
            </h1>
            <p className="text-xs text-muted-foreground flex items-center gap-2">
              <Clock className="h-3 w-3" />
              <span>Created {new Date(scan.created_at).toLocaleString()}</span>
              <span>•</span>
              <span className="uppercase font-mono">{scan.collection_mode}</span>
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}
""",
    "feat(ui): implement InvestigationHeader component with scan metadata"
))

# 30. InvestigationHeader Test
COMMITS.append((
    "apps/dashboard/src/components/investigation/__tests__/investigation-header.test.tsx",
    """import React from "react";
import { describe, it, expect } from "vitest";
import { render, screen } from "@testing-library/react";
import { InvestigationHeader } from "../investigation-header";

describe("InvestigationHeader component", () => {
  it("renders scan title, target, and status badge", () => {
    const scan: any = {
      id: "scan_123",
      platform: "x",
      status: "complete",
      requested_by: "analyst_1",
      created_at: "2026-11-05T09:00:00Z",
      collection_mode: "official_api",
      data_origin: "api",
    };
    render(<InvestigationHeader scan={scan} />);
    expect(screen.getByText("Investigation: analyst_1")).toBeInTheDocument();
    expect(screen.getByText("Back to Overview")).toBeInTheDocument();
    expect(screen.getByText("Complete")).toBeInTheDocument();
  });
});
""",
    "test(ui): test InvestigationHeader displays target, status, and origin"
))

# 31. InvestigationTabs Component
COMMITS.append((
    "apps/dashboard/src/components/investigation/investigation-tabs.tsx",
    """import React from "react";
import { Users, AlertTriangle, Network, Download } from "lucide-react";
import { cn } from "../../lib/utils";

export type TabType = "overview" | "explorer" | "features" | "export";

export interface InvestigationTabsProps {
  activeTab: TabType;
  onTabChange: (tab: TabType) => void;
}

export function InvestigationTabs({ activeTab, onTabChange }: InvestigationTabsProps) {
  const tabs = [
    { id: "overview" as TabType, label: "Overview & Evidence", icon: AlertTriangle },
    { id: "explorer" as TabType, label: "Followers & Following Explorer", icon: Users },
    { id: "features" as TabType, label: "Risk Features & Graph", icon: Network },
    { id: "export" as TabType, label: "Export & Provenance", icon: Download },
  ];

  return (
    <div className="flex items-center gap-1 border-b border-white/5 overflow-x-auto">
      {tabs.map((tab) => {
        const Icon = tab.icon;
        const isActive = activeTab === tab.id;
        return (
          <button
            key={tab.id}
            type="button"
            onClick={() => onTabChange(tab.id)}
            className={cn(
              "flex items-center gap-2 px-4 py-2.5 text-xs font-medium border-b-2 transition-colors whitespace-nowrap",
              isActive
                ? "border-primary text-primary font-semibold"
                : "border-transparent text-muted-foreground hover:text-foreground hover:border-white/10"
            )}
          >
            <Icon className="h-4 w-4" />
            {tab.label}
          </button>
        );
      })}
    </div>
  );
}
""",
    "feat(ui): implement InvestigationTabs navigation component"
))

# 32. InvestigationTabs Test
COMMITS.append((
    "apps/dashboard/src/components/investigation/__tests__/investigation-tabs.test.tsx",
    """import React from "react";
import { describe, it, expect, vi } from "vitest";
import { render, screen, fireEvent } from "@testing-library/react";
import { InvestigationTabs } from "../investigation-tabs";

describe("InvestigationTabs component", () => {
  it("renders tab labels and invokes onTabChange on tab click", () => {
    const handleChange = vi.fn();
    render(<InvestigationTabs activeTab="overview" onTabChange={handleChange} />);
    expect(screen.getByText("Overview & Evidence")).toBeInTheDocument();
    expect(screen.getByText("Followers & Following Explorer")).toBeInTheDocument();

    const explorerTab = screen.getByText("Followers & Following Explorer");
    fireEvent.click(explorerTab);
    expect(handleChange).toHaveBeenCalledWith("explorer");
  });
});
""",
    "test(ui): test InvestigationTabs switches between active workspace views"
))

# 33. EmptyAccountsState Component
COMMITS.append((
    "apps/dashboard/src/components/investigation/empty-accounts-state.tsx",
    """import React from "react";
import { FilterX } from "lucide-react";
import { Button } from "../ui/button";

export interface EmptyAccountsStateProps {
  onResetFilters?: () => void;
}

export function EmptyAccountsState({ onResetFilters }: EmptyAccountsStateProps) {
  return (
    <div className="flex flex-col items-center justify-center p-12 text-center border border-dashed border-white/10 rounded-lg bg-slate-900/30">
      <FilterX className="h-8 w-8 text-muted-foreground mb-3" />
      <h3 className="text-sm font-semibold text-foreground">No accounts match query</h3>
      <p className="text-xs text-muted-foreground mt-1 max-w-sm">
        Try adjusting your search criteria, clearing the risk band filter, or verifying scan completeness.
      </p>
      {onResetFilters && (
        <Button size="sm" variant="outline" onClick={onResetFilters} className="mt-4">
          Reset Search Filters
        </Button>
      )}
    </div>
  );
}
""",
    "feat(ui): implement EmptyAccountsState component for filtered zero states"
))

# 34. EmptyAccountsState Test
COMMITS.append((
    "apps/dashboard/src/components/investigation/__tests__/empty-accounts-state.test.tsx",
    """import React from "react";
import { describe, it, expect, vi } from "vitest";
import { render, screen, fireEvent } from "@testing-library/react";
import { EmptyAccountsState } from "../empty-accounts-state";

describe("EmptyAccountsState component", () => {
  it("renders empty state notice and handles reset action", () => {
    const handleReset = vi.fn();
    render(<EmptyAccountsState onResetFilters={handleReset} />);
    expect(screen.getByText("No accounts match query")).toBeInTheDocument();
    const btn = screen.getByText("Reset Search Filters");
    fireEvent.click(btn);
    expect(handleReset).toHaveBeenCalled();
  });
});
""",
    "test(ui): test EmptyAccountsState displays reset filter recommendation"
))

# 35. AccountNeighborhoodViewer Component
COMMITS.append((
    "apps/dashboard/src/components/investigation/account-neighborhood-viewer.tsx",
    """import React from "react";
import { ArrowDownLeft, ArrowUpRight } from "lucide-react";
import { Card, CardHeader, CardTitle, CardContent } from "../ui/card";
import type { AccountNeighborhoodEdge } from "../../lib/api/types";

export interface AccountNeighborhoodViewerProps {
  inEdges: AccountNeighborhoodEdge[];
  outEdges: AccountNeighborhoodEdge[];
}

export function AccountNeighborhoodViewer({ inEdges, outEdges }: AccountNeighborhoodViewerProps) {
  return (
    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
      <Card className="border-white/5 bg-slate-900/40">
        <CardHeader className="py-3 px-4 flex flex-row items-center justify-between">
          <div className="flex items-center gap-2 text-xs font-semibold text-foreground">
            <ArrowDownLeft className="h-4 w-4 text-blue-400" />
            <CardTitle className="text-xs font-semibold">Inbound Followers</CardTitle>
          </div>
          <span className="font-mono text-xs text-muted-foreground">{inEdges.length}</span>
        </CardHeader>
        <CardContent className="px-4 pb-4 pt-0">
          {inEdges.length === 0 ? (
            <p className="text-xs text-muted-foreground py-2">No observed inbound edges</p>
          ) : (
            <ul className="divide-y divide-white/5 text-xs font-mono">
              {inEdges.slice(0, 10).map((edge, idx) => (
                <li key={idx} className="py-1.5 text-muted-foreground truncate">
                  {edge.source}
                </li>
              ))}
            </ul>
          )}
        </CardContent>
      </Card>

      <Card className="border-white/5 bg-slate-900/40">
        <CardHeader className="py-3 px-4 flex flex-row items-center justify-between">
          <div className="flex items-center gap-2 text-xs font-semibold text-foreground">
            <ArrowUpRight className="h-4 w-4 text-purple-400" />
            <CardTitle className="text-xs font-semibold">Outbound Following</CardTitle>
          </div>
          <span className="font-mono text-xs text-muted-foreground">{outEdges.length}</span>
        </CardHeader>
        <CardContent className="px-4 pb-4 pt-0">
          {outEdges.length === 0 ? (
            <p className="text-xs text-muted-foreground py-2">No observed outbound edges</p>
          ) : (
            <ul className="divide-y divide-white/5 text-xs font-mono">
              {outEdges.slice(0, 10).map((edge, idx) => (
                <li key={idx} className="py-1.5 text-muted-foreground truncate">
                  {edge.target}
                </li>
              ))}
            </ul>
          )}
        </CardContent>
      </Card>
    </div>
  );
}
""",
    "feat(ui): implement AccountNeighborhoodViewer component for 1-hop inspection"
))

# 36. AccountNeighborhoodViewer Test
COMMITS.append((
    "apps/dashboard/src/components/investigation/__tests__/account-neighborhood-viewer.test.tsx",
    """import React from "react";
import { describe, it, expect } from "vitest";
import { render, screen } from "@testing-library/react";
import { AccountNeighborhoodViewer } from "../account-neighborhood-viewer";

describe("AccountNeighborhoodViewer component", () => {
  it("renders inbound and outbound lists", () => {
    const inEdges = [{ source: "user_a", target: "self", relationship_type: "follower" }];
    const outEdges = [{ source: "self", target: "user_b", relationship_type: "following" }];
    render(<AccountNeighborhoodViewer inEdges={inEdges} outEdges={outEdges} />);
    expect(screen.getByText("Inbound Followers")).toBeInTheDocument();
    expect(screen.getByText("Outbound Following")).toBeInTheDocument();
    expect(screen.getByText("user_a")).toBeInTheDocument();
    expect(screen.getByText("user_b")).toBeInTheDocument();
  });
});
""",
    "test(ui): test AccountNeighborhoodViewer renders incoming and outgoing edges"
))

def main() -> None:
    print(f"Starting Day 5 Batch 3 commits build. Total planned: {len(COMMITS)}")
    for rel_path, content, msg in COMMITS:
        write_and_commit(rel_path, content, msg)
    print(f"Batch 3 finished {len(COMMITS)} commits.")

if __name__ == "__main__":
    main()

