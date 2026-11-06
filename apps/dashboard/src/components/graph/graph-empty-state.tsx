"use client";

import React from "react";

export interface GraphEmptyStateProps {
  onResetFilters?: () => void;
}

export function GraphEmptyState({ onResetFilters }: GraphEmptyStateProps) {
  return (
    <div
      data-testid="graph-empty-state"
      className="flex flex-col items-center justify-center p-8 bg-slate-950/60 border border-slate-800 rounded-lg text-center min-h-[350px]"
    >
      <div className="w-12 h-12 rounded-full bg-slate-800 flex items-center justify-center text-slate-400 mb-3 text-xl">
        &#9874;
      </div>
      <h3 className="text-sm font-semibold text-slate-200 mb-1">No Graph Nodes Match Active Filters</h3>
      <p className="text-xs text-slate-400 max-w-sm mb-4">
        Try adjusting your risk band filters, lowering the minimum score threshold, or clearing the search query.
      </p>
      {onResetFilters && (
        <button
          type="button"
          onClick={onResetFilters}
          className="px-3 py-1.5 text-xs font-medium rounded bg-blue-600 hover:bg-blue-500 text-white transition"
        >
          Reset All Filters
        </button>
      )}
    </div>
  );
}
