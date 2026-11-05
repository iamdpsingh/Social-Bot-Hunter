import React from "react";
import { ContributingSignalBar } from "./contributing-signal-bar";

export interface EvidenceItemRowProps {
  signal: {
    signal: string;
    weight: number;
    value: number;
    description?: string;
  };
}

export function EvidenceItemRow({ signal }: EvidenceItemRowProps) {
  return (
    <div className="py-3 flex flex-col sm:flex-row sm:items-center justify-between gap-2">
      <div className="space-y-0.5">
        <div className="flex items-center gap-2">
          <span className="font-mono text-xs font-semibold text-foreground">{signal.signal}</span>
          <span className="text-[10px] text-muted-foreground uppercase tracking-wider bg-white/5 px-1.5 py-0.5 rounded">
            Weight: {Math.round(signal.weight * 100)}%
          </span>
        </div>
        {signal.description && (
          <p className="text-xs text-muted-foreground">{signal.description}</p>
        )}
      </div>

      <div className="w-full sm:w-44 shrink-0">
        <ContributingSignalBar value={signal.value} weight={signal.weight} />
      </div>
    </div>
  );
}
