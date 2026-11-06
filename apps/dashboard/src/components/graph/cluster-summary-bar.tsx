"use client";

import React from "react";
import type { ClusterRecord } from "../../lib/hooks/use-graph-clusters";

export interface ClusterSummaryBarProps {
  clusters: ClusterRecord[];
  activeClusterId?: string;
  onSelectCluster: (clusterId: string) => void;
  onClearCluster: () => void;
}

export function ClusterSummaryBar({
  clusters,
  activeClusterId,
  onSelectCluster,
  onClearCluster,
}: ClusterSummaryBarProps) {
  if (clusters.length === 0) return null;

  return (
    <div
      data-testid="cluster-summary-bar"
      className="flex items-center gap-2 overflow-x-auto py-2 text-xs"
      aria-label="Detected coordinated bot clusters strip"
    >
      <span className="text-slate-400 font-medium whitespace-nowrap">Bot Clusters:</span>

      {clusters.map((c) => {
        const isActive = c.id === activeClusterId;
        return (
          <button
            key={c.id}
            type="button"
            onClick={() => onSelectCluster(c.id)}
            className={`flex items-center gap-1.5 px-2.5 py-1 rounded-full whitespace-nowrap transition font-mono ${
              isActive
                ? "bg-purple-600 text-white font-semibold ring-2 ring-purple-400"
                : "bg-slate-800 hover:bg-slate-700 text-slate-300 border border-slate-700"
            }`}
          >
            <span>{c.id}</span>
            <span className="px-1.5 py-0.2 rounded-full bg-slate-900/60 text-[10px]">
              {c.member_count} bots
            </span>
          </button>
        );
      })}

      {activeClusterId && (
        <button
          type="button"
          onClick={onClearCluster}
          className="text-slate-400 hover:text-slate-200 underline text-xs whitespace-nowrap ml-1"
        >
          Clear filter
        </button>
      )}
    </div>
  );
}
