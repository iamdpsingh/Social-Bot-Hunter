"use client";

import React from "react";

export interface ClusterFilterPillProps {
  clusterId: string;
  onClear: () => void;
}

export function ClusterFilterPill({ clusterId, onClear }: ClusterFilterPillProps) {
  if (!clusterId) return null;

  return (
    <div
      data-testid="cluster-filter-pill"
      className="inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full bg-purple-900/40 border border-purple-700 text-purple-300 text-xs font-mono"
    >
      <span>Cluster: {clusterId}</span>
      <button
        type="button"
        onClick={onClear}
        className="hover:text-white leading-none font-sans"
        aria-label="Remove cluster filter"
      >
        &times;
      </button>
    </div>
  );
}
