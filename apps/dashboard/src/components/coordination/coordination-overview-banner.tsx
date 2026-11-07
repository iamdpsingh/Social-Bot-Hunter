"use client";

import React from "react";
import type { CoordinationSummaryResponse } from "../../lib/api/types";

interface CoordinationOverviewBannerProps {
  coordination: CoordinationSummaryResponse;
}

export function CoordinationOverviewBanner({ coordination }: CoordinationOverviewBannerProps) {
  const scorePct = Math.round(coordination.overall_coordination_score * 100);
  const isHigh = scorePct >= 60;
  const isMed = scorePct >= 30 && scorePct < 60;

  return (
    <div
      data-testid="coordination-overview-banner"
      className="p-6 rounded-2xl border border-border bg-gradient-to-r from-card via-card to-muted/20 shadow-sm"
    >
      <div className="flex flex-col md:flex-row items-start md:items-center justify-between gap-6">
        <div>
          <div className="flex items-center gap-3">
            <h3 className="text-xl font-bold text-foreground">Coordinated Campaign Detection</h3>
            <span
              className={`text-xs px-2.5 py-0.5 rounded-full font-bold uppercase tracking-wider ${
                isHigh
                  ? "bg-red-500/10 text-red-500 border border-red-500/30"
                  : isMed
                  ? "bg-amber-500/10 text-amber-500 border border-amber-500/30"
                  : "bg-emerald-500/10 text-emerald-500 border border-emerald-500/30"
              }`}
            >
              {isHigh ? "High Coordination" : isMed ? "Moderate Coordination" : "Minimal Coordination"}
            </span>
          </div>
          <p className="text-sm text-muted-foreground mt-1 max-w-2xl">
            Correlating SimHash text fingerprinting, synchronized temporal burst intervals,
            and shared follower network graph topologies to detect astroturfing campaigns.
          </p>
        </div>

        <div className="flex items-center gap-6 self-stretch md:self-auto justify-between md:justify-end">
          <div className="text-center">
            <span className="block text-2xl font-black text-foreground">
              {coordination.total_coordinated_accounts}
            </span>
            <span className="text-xs text-muted-foreground uppercase font-medium">Coordinated Bots</span>
          </div>
          <div className="h-10 w-px bg-border" />
          <div className="text-center">
            <span
              className={`block text-3xl font-black ${
                isHigh ? "text-red-500" : isMed ? "text-amber-500" : "text-emerald-500"
              }`}
            >
              {scorePct}%
            </span>
            <span className="text-xs text-muted-foreground uppercase font-medium">Confidence Score</span>
          </div>
        </div>
      </div>
    </div>
  );
}
