import React from "react";

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
