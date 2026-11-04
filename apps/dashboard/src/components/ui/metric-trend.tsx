import React from "react";
import { TrendingUp, TrendingDown, Minus } from "lucide-react";
import { cn } from "../../lib/utils";

export interface MetricTrendProps {
  value: number;
  direction?: "up" | "down" | "neutral";
  label?: string;
  className?: string;
}

export function MetricTrend({ value, direction = "neutral", label, className }: MetricTrendProps) {
  const isUp = direction === "up";
  const isDown = direction === "down";

  return (
    <div
      className={cn(
        "inline-flex items-center gap-1 text-xs font-medium",
        isUp && "text-emerald-400",
        isDown && "text-red-400",
        !isUp && !isDown && "text-muted-foreground",
        className
      )}
    >
      {isUp && <TrendingUp className="h-3.5 w-3.5" data-testid="trend-up" />}
      {isDown && <TrendingDown className="h-3.5 w-3.5" data-testid="trend-down" />}
      {!isUp && !isDown && <Minus className="h-3.5 w-3.5" data-testid="trend-neutral" />}
      <span>{Math.abs(value)}%</span>
      {label && <span className="text-[11px] text-muted-foreground ml-0.5">{label}</span>}
    </div>
  );
}
