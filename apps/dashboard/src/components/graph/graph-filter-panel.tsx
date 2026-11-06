"use client";

import React from "react";

export interface GraphFilterPanelProps {
  searchQuery: string;
  onSearchChange: (q: string) => void;
  selectedBand: string;
  onBandChange: (band: string) => void;
  minScore: number;
  onMinScoreChange: (score: number) => void;
  clusterFilter: string;
  onClusterChange: (c: string) => void;
  clusterOptions?: Array<{ id: string; label: string }>;
  totalNodes: number;
  filteredNodes: number;
  onClearFilters: () => void;
}

export function GraphFilterPanel({
  searchQuery,
  onSearchChange,
  selectedBand,
  onBandChange,
  minScore,
  onMinScoreChange,
  clusterFilter,
  onClusterChange,
  clusterOptions = [],
  totalNodes,
  filteredNodes,
  onClearFilters,
}: GraphFilterPanelProps) {
  return (
    <div
      data-testid="graph-filter-panel"
      className="flex flex-wrap items-center gap-3 bg-slate-900/90 border border-slate-800 p-3 rounded-lg text-xs"
    >
      <div className="flex-1 min-w-[160px]">
        <input
          type="text"
          value={searchQuery}
          onChange={(e) => onSearchChange(e.target.value)}
          placeholder="Search accounts or IDs..."
          className="w-full bg-slate-800 border border-slate-700 text-slate-200 placeholder-slate-500 rounded px-2.5 py-1.5 focus:outline-none focus:ring-1 focus:ring-blue-500"
          aria-label="Search graph accounts"
        />
      </div>

      <div className="flex items-center gap-1.5">
        <label htmlFor="risk-band-filter" className="text-slate-400">
          Band:
        </label>
        <select
          id="risk-band-filter"
          value={selectedBand}
          onChange={(e) => onBandChange(e.target.value)}
          className="bg-slate-800 border border-slate-700 text-slate-200 rounded px-2 py-1.5"
        >
          <option value="">All Bands</option>
          <option value="critical">Critical</option>
          <option value="high">High</option>
          <option value="medium">Medium</option>
          <option value="low">Low</option>
          <option value="insufficient_evidence">Insufficient</option>
        </select>
      </div>

      <div className="flex items-center gap-2">
        <label htmlFor="min-score-slider" className="text-slate-400">
          Min Score: <span className="font-mono text-slate-200">{(minScore * 100).toFixed(0)}%</span>
        </label>
        <input
          id="min-score-slider"
          type="range"
          min="0"
          max="1"
          step="0.05"
          value={minScore}
          onChange={(e) => onMinScoreChange(parseFloat(e.target.value))}
          className="w-20 accent-blue-500 cursor-pointer"
        />
      </div>

      {clusterOptions.length > 0 && (
        <div className="flex items-center gap-1.5">
          <label htmlFor="cluster-filter" className="text-slate-400">
            Cluster:
          </label>
          <select
            id="cluster-filter"
            value={clusterFilter}
            onChange={(e) => onClusterChange(e.target.value)}
            className="bg-slate-800 border border-slate-700 text-slate-200 rounded px-2 py-1.5 max-w-[140px] truncate"
          >
            <option value="">All Clusters</option>
            {clusterOptions.map((c) => (
              <option key={c.id} value={c.id}>
                {c.label}
              </option>
            ))}
          </select>
        </div>
      )}

      <div className="flex items-center gap-2 ml-auto text-slate-400">
        <span>
          Showing <strong className="text-slate-200">{filteredNodes}</strong> / {totalNodes}
        </span>
        <button
          type="button"
          onClick={onClearFilters}
          className="text-blue-400 hover:text-blue-300 underline font-medium"
        >
          Reset
        </button>
      </div>
    </div>
  );
}
