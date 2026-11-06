"use client";

import React from "react";

export interface GraphScaleAlertProps {
  nodeCount: number;
  onSwitchToTable: () => void;
}

export function GraphScaleAlert({ nodeCount, onSwitchToTable }: GraphScaleAlertProps) {
  if (nodeCount <= 5000) return null;

  return (
    <div
      data-testid="graph-scale-alert"
      className="flex items-center justify-between gap-3 p-3 bg-amber-950/40 border border-amber-800/80 rounded-lg text-amber-200 text-xs"
      role="alert"
    >
      <div className="flex items-center gap-2">
        <span className="text-amber-400 font-bold">&#9888;</span>
        <span>
          Large network detected (<strong>{nodeCount.toLocaleString()}</strong> nodes). WebGL/Canvas rendering may be throttled.
        </span>
      </div>
      <button
        type="button"
        onClick={onSwitchToTable}
        className="px-2.5 py-1 rounded bg-amber-800 hover:bg-amber-700 text-white font-medium whitespace-nowrap transition"
      >
        Switch to Table View
      </button>
    </div>
  );
}
