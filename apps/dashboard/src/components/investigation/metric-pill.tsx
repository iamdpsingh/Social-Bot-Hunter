import React from "react";
import { cn } from "../../lib/utils";

export interface MetricPillProps {
  label: string;
  value: string | number;
  highlight?: boolean;
  className?: string;
}

export function MetricPill({ label, value, highlight, className }: MetricPillProps) {
  return (
    <div
      className={cn(
        "inline-flex items-center gap-1.5 rounded-lg border border-white/5 bg-white/5 px-3 py-1.5 text-xs",
        highlight && "border-primary/20 bg-primary/10 text-primary",
        className
      )}
    >
      <span className="text-muted-foreground">{label}:</span>
      <span className="font-semibold text-foreground font-mono">{value}</span>
    </div>
  );
}
