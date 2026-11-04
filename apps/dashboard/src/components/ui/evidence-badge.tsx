import React from "react";
import { cn } from "../../lib/utils";

export interface EvidenceBadgeProps {
  label: string;
  confidence: number;
  className?: string;
}

export function EvidenceBadge({ label, confidence, className }: EvidenceBadgeProps) {
  const pct = Math.round(confidence * 100);
  return (
    <span
      className={cn(
        "inline-flex items-center gap-1.5 rounded-full border border-primary/20 bg-primary/10 px-2.5 py-0.5 text-xs font-medium text-primary",
        className
      )}
    >
      <span>{label}</span>
      <span className="font-mono text-[10px] opacity-75">{pct}%</span>
    </span>
  );
}
