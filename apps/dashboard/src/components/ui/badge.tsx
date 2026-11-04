import React from "react";
import { cn } from "../../lib/utils";
import { type RiskBand, RISK_BANDS, getRiskBand } from "../../tokens/risk";
import type { ScanStatus } from "../../lib/api/types";

export interface BadgeProps extends React.HTMLAttributes<HTMLSpanElement> {
  variant?: "default" | "secondary" | "destructive" | "warning" | "success" | "outline";
}

export function Badge({ className, variant = "default", ...props }: BadgeProps) {
  const variants = {
    default: "bg-primary text-primary-foreground",
    secondary: "bg-secondary text-secondary-foreground",
    destructive: "bg-destructive text-destructive-foreground",
    warning: "bg-amber-500/15 text-amber-500 border border-amber-500/30",
    success: "bg-emerald-500/15 text-emerald-500 border border-emerald-500/30",
    outline: "text-foreground border border-border",
  };

  return (
    <span
      className={cn(
        "inline-flex items-center rounded-full px-2.5 py-0.5 text-xs font-semibold transition-colors focus:outline-none focus:ring-2 focus:ring-ring focus:ring-offset-2",
        variants[variant],
        className
      )}
      {...props}
    />
  );
}

export function RiskBadge({ score, band }: { score?: number | null; band?: RiskBand }) {
  const def = band ? RISK_BANDS[band] : getRiskBand(score);

  return (
    <span
      className="inline-flex items-center gap-1.5 rounded-full px-2.5 py-0.5 text-xs font-semibold"
      style={{
        backgroundColor: def.bgColor,
        color: def.color,
        border: `1px solid ${def.borderColor}`,
      }}
    >
      <span
        className="h-1.5 w-1.5 rounded-full"
        style={{ backgroundColor: def.color }}
        aria-hidden="true"
      />
      {def.label}
      {score !== undefined && score !== null && score >= 0 && (
        <span className="opacity-80 font-mono text-[10px]">({Math.round(score * 100)}%)</span>
      )}
    </span>
  );
}

export function ScanStatusBadge({ status }: { status: ScanStatus }) {
  const statusStyles: Record<ScanStatus, { bg: string; text: string; border: string; label: string }> = {
    pending: {
      bg: "bg-slate-500/15",
      text: "text-slate-400",
      border: "border-slate-500/30",
      label: "Pending",
    },
    running: {
      bg: "bg-blue-500/15",
      text: "text-blue-400",
      border: "border-blue-500/30",
      label: "Running",
    },
    complete: {
      bg: "bg-emerald-500/15",
      text: "text-emerald-400",
      border: "border-emerald-500/30",
      label: "Complete",
    },
    partial: {
      bg: "bg-amber-500/15",
      text: "text-amber-400",
      border: "border-amber-500/30",
      label: "Partial",
    },
    failed: {
      bg: "bg-red-500/15",
      text: "text-red-400",
      border: "border-red-500/30",
      label: "Failed",
    },
    cancelled: {
      bg: "bg-zinc-500/15",
      text: "text-zinc-400",
      border: "border-zinc-500/30",
      label: "Cancelled",
    },
  };

  const current = statusStyles[status] || statusStyles.pending;

  return (
    <span
      className={cn(
        "inline-flex items-center gap-1.5 rounded-full px-2.5 py-0.5 text-xs font-medium border",
        current.bg,
        current.text,
        current.border
      )}
    >
      <span className={cn("h-1.5 w-1.5 rounded-full", current.text.replace("text-", "bg-"))} />
      {current.label}
    </span>
  );
}
