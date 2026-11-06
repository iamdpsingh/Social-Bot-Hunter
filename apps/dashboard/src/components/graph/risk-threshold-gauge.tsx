"use client";

import React from "react";

export interface RiskThresholdGaugeProps {
  minScore: number;
}

export function RiskThresholdGauge({ minScore }: RiskThresholdGaugeProps) {
  const percent = Math.round(minScore * 100);
  const color =
    minScore >= 0.8
      ? "#ef4444"
      : minScore >= 0.6
      ? "#f97316"
      : minScore >= 0.4
      ? "#eab308"
      : "#22c55e";

  return (
    <div data-testid="risk-threshold-gauge" className="flex items-center gap-2 text-xs">
      <div className="w-12 bg-slate-800 h-2 rounded-full overflow-hidden">
        <div
          className="h-full rounded-full transition-all duration-200"
          style={{ width: `${percent}%`, backgroundColor: color }}
        />
      </div>
      <span className="font-mono text-slate-300">{percent}%</span>
    </div>
  );
}
