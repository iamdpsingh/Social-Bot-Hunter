"use client";

import React from "react";
import { Activity, Clock, Repeat, UserCheck, Shield } from "lucide-react";

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
    { label: "Activity Timing", score: timingScore, icon: Clock },
    { label: "Text Repetition", score: textRepetitionScore, icon: Repeat },
    { label: "Network Anomaly", score: networkAnomalyScore, icon: Activity },
    { label: "Profile Pattern", score: profileScore, icon: UserCheck },
  ];

  return (
    <div className="rounded-lg border border-border bg-card p-4 space-y-3" data-testid="signal-radar-preview">
      <div className="flex items-center justify-between">
        <h4 className="text-xs font-semibold text-foreground uppercase tracking-wider flex items-center gap-1.5">
          <Shield className="h-3.5 w-3.5 text-primary" />
          Detection Signal Vectors
        </h4>
        <span className="text-[11px] text-muted-foreground">Heuristic Breakdown</span>
      </div>

      <div className="space-y-2">
        {indicators.map((ind) => {
          const Icon = ind.icon;
          const percentage = Math.round(ind.score * 100);
          const colorClass =
            percentage > 70 ? "bg-rose-500" : percentage > 40 ? "bg-amber-500" : "bg-emerald-500";

          return (
            <div key={ind.label} className="space-y-1">
              <div className="flex items-center justify-between text-xs">
                <span className="flex items-center gap-1.5 text-muted-foreground">
                  <Icon className="h-3 w-3" />
                  {ind.label}
                </span>
                <span className="font-mono font-medium text-foreground">{percentage}%</span>
              </div>
              <div className="h-1.5 w-full bg-muted rounded-full overflow-hidden">
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
