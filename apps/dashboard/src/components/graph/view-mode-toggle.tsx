"use client";

import React from "react";

export type GraphViewMode = "canvas" | "table";

export interface ViewModeToggleProps {
  viewMode: GraphViewMode;
  onViewModeChange: (mode: GraphViewMode) => void;
}

export function ViewModeToggle({ viewMode, onViewModeChange }: ViewModeToggleProps) {
  return (
    <div
      data-testid="view-mode-toggle"
      className="inline-flex items-center p-1 bg-slate-900 border border-slate-800 rounded-lg text-xs"
      role="group"
      aria-label="Graph visualization view toggle"
    >
      <button
        type="button"
        onClick={() => onViewModeChange("canvas")}
        className={`px-3 py-1.5 rounded-md font-medium transition ${
          viewMode === "canvas"
            ? "bg-blue-600 text-white shadow-sm"
            : "text-slate-400 hover:text-slate-200"
        }`}
        aria-pressed={viewMode === "canvas"}
      >
        Interactive Canvas
      </button>
      <button
        type="button"
        onClick={() => onViewModeChange("table")}
        className={`px-3 py-1.5 rounded-md font-medium transition ${
          viewMode === "table"
            ? "bg-blue-600 text-white shadow-sm"
            : "text-slate-400 hover:text-slate-200"
        }`}
        aria-pressed={viewMode === "table"}
      >
        Accessible Table
      </button>
    </div>
  );
}
