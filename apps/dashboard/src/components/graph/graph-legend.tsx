"use client";

import React from "react";
import { GRAPH_NODE_COLORS } from "../../tokens/graph";

export function GraphLegend() {
  const bands = [
    { label: "Critical", key: "critical" },
    { label: "High", key: "high" },
    { label: "Medium", key: "medium" },
    { label: "Low", key: "low" },
    { label: "Insufficient", key: "insufficient_evidence" },
  ];

  return (
    <div
      data-testid="graph-legend"
      className="flex flex-wrap items-center gap-3 text-xs bg-slate-900/80 border border-slate-800/80 px-3 py-1.5 rounded-lg text-slate-300"
      aria-label="Graph node risk legend"
    >
      <span className="text-slate-400 font-medium">Risk:</span>
      {bands.map((b) => (
        <div key={b.key} className="flex items-center gap-1.5">
          <span
            className="inline-block w-2.5 h-2.5 rounded-full"
            style={{ backgroundColor: GRAPH_NODE_COLORS[b.key]?.bg }}
            aria-hidden="true"
          />
          <span>{b.label}</span>
        </div>
      ))}
      <div className="h-3 w-px bg-slate-700" aria-hidden="true" />
      <span className="text-slate-400">Arrow: Follower &rarr; Following</span>
    </div>
  );
}
