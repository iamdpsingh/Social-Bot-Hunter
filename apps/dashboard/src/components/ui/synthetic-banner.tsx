import React from "react";
import { AlertTriangle } from "lucide-react";
import { cn } from "../../lib/utils";

export interface SyntheticDataBannerProps {
  className?: string;
  subtext?: string;
}

export function SyntheticDataBanner({ className, subtext }: SyntheticDataBannerProps) {
  return (
    <div
      role="status"
      aria-label="Synthetic Data Warning"
      className={cn(
        "flex items-center justify-between gap-3 px-4 py-2.5 bg-amber-500/10 border border-amber-500/25 rounded-lg text-amber-400 text-xs",
        className
      )}
    >
      <div className="flex items-center gap-2.5">
        <AlertTriangle className="h-4 w-4 shrink-0 text-amber-400" />
        <div>
          <span className="font-bold tracking-wider uppercase text-[11px] bg-amber-500/20 px-1.5 py-0.5 rounded mr-2">
            Synthetic Demo Data
          </span>
          <span>
            {subtext ||
              "This dataset is synthetically generated for verification and evaluation purposes. Do not treat risk scores as empirical accusations against live accounts."}
          </span>
        </div>
      </div>
      <span className="font-mono text-[11px] opacity-75 shrink-0 hidden sm:inline-block">
        PROVENANCE: SYNTHETIC
      </span>
    </div>
  );
}
