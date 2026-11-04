import React from "react";
import { cn } from "../../lib/utils";

export interface ProgressBarProps {
  value: number; // 0 to 100
  max?: number;
  label?: string;
  subtext?: string;
  variant?: "primary" | "success" | "warning" | "destructive";
  className?: string;
}

export function ProgressBar({
  value,
  max = 100,
  label,
  subtext,
  variant = "primary",
  className,
}: ProgressBarProps) {
  const percentage = Math.min(Math.max((value / max) * 100, 0), 100);

  const variants = {
    primary: "bg-primary",
    success: "bg-emerald-500",
    warning: "bg-amber-500",
    destructive: "bg-red-500",
  };

  return (
    <div className={cn("w-full space-y-1.5", className)}>
      {(label || subtext) && (
        <div className="flex items-center justify-between text-xs">
          {label && <span className="font-medium text-foreground">{label}</span>}
          {subtext && <span className="font-mono text-muted-foreground">{subtext}</span>}
        </div>
      )}
      <div className="relative h-2 w-full overflow-hidden rounded-full bg-white/10">
        <div
          className={cn("h-full transition-all duration-300 rounded-full", variants[variant])}
          style={{ width: `${percentage}%` }}
          role="progressbar"
          aria-valuenow={Math.round(percentage)}
          aria-valuemin={0}
          aria-valuemax={100}
        />
      </div>
    </div>
  );
}
