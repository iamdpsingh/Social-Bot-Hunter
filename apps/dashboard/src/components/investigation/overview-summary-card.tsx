"use client";

import React from "react";
import { ShieldAlert, Users, TrendingUp, AlertTriangle } from "lucide-react";

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
  const botRatio = totalAccounts > 0 ? ((botAccounts / totalAccounts) * 100).toFixed(1) : "0.0";

  return (
    <div className="grid grid-cols-2 lg:grid-cols-4 gap-4" data-testid="overview-summary-card">
      <div className="rounded-lg border border-border bg-card p-4 space-y-1">
        <div className="flex items-center justify-between text-muted-foreground">
          <span className="text-xs font-medium uppercase tracking-wider">Total Accounts</span>
          <Users className="h-4 w-4" />
        </div>
        <div className="text-2xl font-bold text-foreground">{totalAccounts.toLocaleString()}</div>
        <div className="text-[11px] text-muted-foreground">Analyzed in investigation</div>
      </div>

      <div className="rounded-lg border border-border bg-card p-4 space-y-1">
        <div className="flex items-center justify-between text-muted-foreground">
          <span className="text-xs font-medium uppercase tracking-wider">Flagged Bots</span>
          <ShieldAlert className="h-4 w-4 text-rose-500" />
        </div>
        <div className="text-2xl font-bold text-rose-500">{botAccounts.toLocaleString()}</div>
        <div className="text-[11px] text-muted-foreground">{botRatio}% flag rate</div>
      </div>

      <div className="rounded-lg border border-border bg-card p-4 space-y-1">
        <div className="flex items-center justify-between text-muted-foreground">
          <span className="text-xs font-medium uppercase tracking-wider">Avg Risk Score</span>
          <TrendingUp className="h-4 w-4 text-amber-500" />
        </div>
        <div className="text-2xl font-bold text-foreground">{avgRiskScore.toFixed(2)}</div>
        <div className="text-[11px] text-muted-foreground">Scale 0.00 – 1.00</div>
      </div>

      <div className="rounded-lg border border-border bg-card p-4 space-y-1">
        <div className="flex items-center justify-between text-muted-foreground">
          <span className="text-xs font-medium uppercase tracking-wider">Critical Alerts</span>
          <AlertTriangle className="h-4 w-4 text-rose-500" />
        </div>
        <div className="text-2xl font-bold text-rose-500">{criticalCount}</div>
        <div className="text-[11px] text-muted-foreground">Requires immediate review</div>
      </div>
    </div>
  );
}
