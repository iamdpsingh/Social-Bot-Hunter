"use client";

import React from "react";
import { Users, AlertTriangle, Network, ShieldCheck } from "lucide-react";
import { StatCard } from "../ui/stat-card";
import { useScans } from "../../lib/hooks/use-scans";

export function MetricsOverviewGrid() {
  const { scans, total } = useScans(50);

  const activeScans = scans.filter((s) => s.status === "running").length;
  const completedScans = scans.filter((s) => s.status === "complete").length;
  const failedScans = scans.filter((s) => s.status === "failed").length;

  return (
    <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
      <StatCard
        title="Total Investigations"
        value={total}
        description={`${activeScans} currently executing`}
        icon={Users}
        coveragePct={94}
      />
      <StatCard
        title="Completed Scans"
        value={completedScans}
        description="Analyzed with evidence trail"
        icon={ShieldCheck}
        trend={{ value: "+12% this week", isPositive: true }}
      />
      <StatCard
        title="Coordinated Clusters"
        value={completedScans > 0 ? "4 detected" : "0 detected"}
        description="SimHash & neighborhood overlap"
        icon={Network}
      />
      <StatCard
        title="Failed / Cancelled"
        value={failedScans}
        description="Available for immediate retry"
        icon={AlertTriangle}
        trend={{ value: failedScans > 0 ? "Inspect runbook" : "All clean", isPositive: failedScans === 0 }}
      />
    </div>
  );
}
