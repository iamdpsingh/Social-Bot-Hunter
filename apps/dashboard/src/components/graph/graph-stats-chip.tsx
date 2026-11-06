"use client";

import React from "react";

export interface GraphStatsChipProps {
  nodeCount: number;
  edgeCount: number;
}

export function GraphStatsChip({ nodeCount, edgeCount }: GraphStatsChipProps) {
  return (
    <div
      data-testid="graph-stats-chip"
      className="inline-flex items-center gap-1.5 px-2.5 py-1 bg-slate-800/90 border border-slate-700/80 rounded-full text-xs text-slate-300 font-mono"
    >
      <span><strong>{nodeCount}</strong> nodes</span>
      <span className="text-slate-500">&bull;</span>
      <span><strong>{edgeCount}</strong> edges</span>
    </div>
  );
}
