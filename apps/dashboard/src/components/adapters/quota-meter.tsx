"use client";

import React from "react";
import { cn } from "../../lib/utils";

interface QuotaMeterProps {
  platform: string;
  dailyLimit: number;
  unitsUsed: number;
  className?: string;
}

export function QuotaMeter({ platform, dailyLimit, unitsUsed, className }: QuotaMeterProps) {
  const percentage = dailyLimit > 0 ? Math.min(100, Math.round((unitsUsed / dailyLimit) * 100)) : 100;
  const isWarning = percentage >= 80 && percentage < 100;
  const isExhausted = percentage >= 100;

  const barColor = isExhausted
    ? "bg-rose-500 shadow-[0_0_12px_rgba(244,63,94,0.4)]"
    : isWarning
    ? "bg-amber-500 shadow-[0_0_12px_rgba(245,158,11,0.4)]"
    : "bg-emerald-500 shadow-[0_0_12px_rgba(16,185,129,0.3)]";

  return (
    <div className={cn("space-y-1.5", className)} data-testid={`quota-meter-${platform}`}>
      <div className="flex items-center justify-between text-xs">
        <span className="font-medium text-muted-foreground capitalize">{platform} Daily Quota</span>
        <span className="font-mono text-[11px] font-semibold text-foreground">
          {unitsUsed.toLocaleString()} / {dailyLimit.toLocaleString()} units ({percentage}%)
        </span>
      </div>

      <div className="h-2 w-full overflow-hidden rounded-full bg-white/5 border border-white/10">
        <div
          className={cn("h-full transition-all duration-500 rounded-full", barColor)}
          style={{ width: `${percentage}%` }}
          role="progressbar"
          aria-valuenow={percentage}
          aria-valuemin={0}
          aria-valuemax={100}
          aria-label={`${platform} API Quota Usage`}
        />
      </div>

      {isWarning && !isExhausted && (
        <p className="text-[11px] text-amber-400/90 font-medium flex items-center gap-1">
          ⚠️ Approaching daily quota ceiling (&gt;80% used)
        </p>
      )}
      {isExhausted && (
        <p className="text-[11px] text-rose-400/90 font-medium flex items-center gap-1">
          ⛔ Daily quota exhausted. Requests paused until midnight UTC.
        </p>
      )}
    </div>
  );
}
