"use client";

import React from "react";
import type { GraphMetricsResponse } from "../../lib/api/types";

export interface GraphMetricsCardProps {
  metrics: GraphMetricsResponse | null;
  loading?: boolean;
}

export function GraphMetricsCard({ metrics, loading = false }: GraphMetricsCardProps) {
  if (loading || !metrics) {
    return (
      <div data-testid="graph-metrics-card-loading" className="grid grid-cols-2 sm:grid-cols-4 gap-2 animate-pulse">
        {[1, 2, 3, 4].map((i) => (
          <div key={i} className="h-14 bg-slate-900 rounded border border-slate-800" />
        ))}
      </div>
    );
  }

  return (
    <div
      data-testid="graph-metrics-card"
      className="grid grid-cols-2 sm:grid-cols-4 gap-3 bg-slate-900/60 border border-slate-800 p-3 rounded-lg text-xs"
    >
      <div>
        <p className="text-slate-400">Total Nodes</p>
        <p className="text-base font-bold text-slate-100">{metrics.node_count.toLocaleString()}</p>
      </div>
      <div>
        <p className="text-slate-400">Directed Edges</p>
        <p className="text-base font-bold text-slate-100">{metrics.edge_count.toLocaleString()}</p>
      </div>
      <div>
        <p className="text-slate-400">Density</p>
        <p className="text-base font-bold text-slate-100">{metrics.density.toFixed(4)}</p>
      </div>
      <div>
        <p className="text-slate-400">Reciprocity</p>
        <p className="text-base font-bold text-slate-100">{(metrics.reciprocity * 100).toFixed(1)}%</p>
      </div>
    </div>
  );
}
