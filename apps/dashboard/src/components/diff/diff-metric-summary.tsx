"use client";

import React from "react";
import type { ScanDiffResponse } from "../../lib/api/types";

interface DiffMetricSummaryProps {
  diff: ScanDiffResponse;
}

export function DiffMetricSummary({ diff }: DiffMetricSummaryProps) {
  const cards = [
    {
      label: "Confirmed Added",
      value: diff.confirmed_additions_count,
      color: "text-emerald-500",
      bg: "bg-emerald-500/10 border-emerald-500/20",
      desc: "Discovered in B, proven absent in A",
    },
    {
      label: "Confirmed Removed",
      value: diff.confirmed_removals_count,
      color: "text-rose-500",
      bg: "bg-rose-500/10 border-rose-500/20",
      desc: "Observed in A, confirmed deleted/unfollowed in B",
    },
    {
      label: "Coverage Gaps",
      value: diff.coverage_gap_additions_count + diff.coverage_gap_removals_count,
      color: "text-amber-500",
      bg: "bg-amber-500/10 border-amber-500/20",
      desc: "Unobserved due to depth or collection limits",
    },
    {
      label: "Risk Escalations",
      value: diff.escalated_risk_count,
      color: "text-purple-500",
      bg: "bg-purple-500/10 border-purple-500/20",
      desc: "Persisting accounts with increased risk",
    },
  ];

  return (
    <div data-testid="diff-metric-summary" className="grid grid-cols-2 lg:grid-cols-4 gap-4">
      {cards.map((card) => (
        <div
          key={card.label}
          className={`p-4 rounded-xl border ${card.bg} shadow-sm flex flex-col justify-between`}
        >
          <div>
            <span className="text-xs font-semibold text-muted-foreground uppercase tracking-wider">
              {card.label}
            </span>
            <div className={`text-2xl font-black mt-1 ${card.color}`}>{card.value}</div>
          </div>
          <p className="text-[11px] text-muted-foreground mt-2">{card.desc}</p>
        </div>
      ))}
    </div>
  );
}
