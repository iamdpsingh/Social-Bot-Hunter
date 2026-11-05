import React from "react";
import { cn } from "../../lib/utils";
import { RISK_GAUGE_TOKENS } from "../../tokens/risk-gauge";
import { RiskBadge } from "../ui/badge";
import type { RiskBand } from "../../tokens/risk";

export interface RiskGaugeProps {
  score: number | null | undefined;
  band?: RiskBand;
  size?: "sm" | "md" | "lg" | number;
  confidence?: number;
  className?: string;
  showBadge?: boolean;
}

export function RiskGauge({
  score,
  band,
  size = "md",
  confidence,
  className,
  showBadge = true,
}: RiskGaugeProps) {
  const cfg = typeof size === "number"
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
      role="meter"
      aria-label="Bot Probability Risk Gauge"
      aria-valuenow={pct}
      aria-valuemin={0}
      aria-valuemax={100}
      aria-valuetext={`${pct}% Risk`}
      className={cn("flex flex-col items-center justify-center gap-2", className)}
    >
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
            strokeDasharray={cfg.radius * 2 * Math.PI}
            strokeDashoffset={strokeDashoffset}
            strokeLinecap="round"
            fill="transparent"
            className="transition-all duration-500 ease-out"
          />
        </svg>

        {/* Center Readout */}
        <div className="absolute flex flex-col items-center justify-center text-center select-none">
          <span className="font-mono font-bold text-foreground text-2xl tracking-tight">
            {pct}%
          </span>
          <span className="text-[10px] text-muted-foreground font-mono uppercase tracking-wider">
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
