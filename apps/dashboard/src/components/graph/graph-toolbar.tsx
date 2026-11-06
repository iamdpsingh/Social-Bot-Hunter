"use client";

import React from "react";
import { LAYOUT_PRESETS, type LayoutPresetId } from "../../tokens/graph";

export interface GraphToolbarProps {
  layoutPreset: LayoutPresetId;
  onChangeLayout: (preset: LayoutPresetId) => void;
  onZoomIn: () => void;
  onZoomOut: () => void;
  onFit: () => void;
  onReset: () => void;
  onToggleHulls?: () => void;
  showHulls?: boolean;
}

export function GraphToolbar({
  layoutPreset,
  onChangeLayout,
  onZoomIn,
  onZoomOut,
  onFit,
  onReset,
  onToggleHulls,
  showHulls = true,
}: GraphToolbarProps) {
  return (
    <div
      data-testid="graph-toolbar"
      className="flex flex-wrap items-center gap-2 bg-slate-900/90 border border-slate-800 p-2 rounded-lg backdrop-blur-sm"
      role="toolbar"
      aria-label="Graph controls toolbar"
    >
      <div className="flex items-center gap-1">
        <button
          type="button"
          onClick={onZoomIn}
          className="px-2.5 py-1 text-xs font-medium rounded bg-slate-800 text-slate-200 hover:bg-slate-700 transition"
          aria-label="Zoom in"
          title="Zoom in"
        >
          +
        </button>
        <button
          type="button"
          onClick={onZoomOut}
          className="px-2.5 py-1 text-xs font-medium rounded bg-slate-800 text-slate-200 hover:bg-slate-700 transition"
          aria-label="Zoom out"
          title="Zoom out"
        >
          -
        </button>
        <button
          type="button"
          onClick={onFit}
          className="px-2.5 py-1 text-xs font-medium rounded bg-slate-800 text-slate-200 hover:bg-slate-700 transition"
          aria-label="Fit to screen"
        >
          Fit
        </button>
        <button
          type="button"
          onClick={onReset}
          className="px-2.5 py-1 text-xs font-medium rounded bg-slate-800 text-slate-200 hover:bg-slate-700 transition"
          aria-label="Reset view"
        >
          Reset
        </button>
      </div>

      <div className="h-4 w-px bg-slate-700" aria-hidden="true" />

      <div className="flex items-center gap-2">
        <label htmlFor="layout-select" className="text-xs text-slate-400">
          Layout:
        </label>
        <select
          id="layout-select"
          value={layoutPreset}
          onChange={(e) => onChangeLayout(e.target.value as LayoutPresetId)}
          className="bg-slate-800 border border-slate-700 text-slate-200 text-xs rounded px-2 py-1 focus:ring-1 focus:ring-blue-500"
        >
          {LAYOUT_PRESETS.map((p) => (
            <option key={p.id} value={p.id}>
              {p.label}
            </option>
          ))}
        </select>
      </div>

      {onToggleHulls && (
        <>
          <div className="h-4 w-px bg-slate-700" aria-hidden="true" />
          <button
            type="button"
            onClick={onToggleHulls}
            className={`px-2.5 py-1 text-xs font-medium rounded transition ${
              showHulls
                ? "bg-purple-900/60 text-purple-300 border border-purple-700"
                : "bg-slate-800 text-slate-400 hover:bg-slate-700"
            }`}
          >
            {showHulls ? "Hulls: On" : "Hulls: Off"}
          </button>
        </>
      )}
    </div>
  );
}
