"use client";

import React from "react";

export interface EdgeDetailPopoverProps {
  sourceId: string;
  targetId: string;
  relationshipType?: string;
  observedAt?: string | null;
  onClose: () => void;
}

export function EdgeDetailPopover({
  sourceId,
  targetId,
  relationshipType = "follows",
  observedAt,
  onClose,
}: EdgeDetailPopoverProps) {
  return (
    <div
      data-testid="edge-detail-popover"
      className="absolute bottom-4 left-4 z-20 w-72 bg-slate-900 border border-slate-700 p-3 rounded-lg shadow-xl text-xs text-slate-200 backdrop-blur-md"
      role="tooltip"
    >
      <div className="flex items-center justify-between pb-2 border-b border-slate-800">
        <span className="font-semibold text-slate-300">Relationship Edge</span>
        <button
          type="button"
          onClick={onClose}
          className="text-slate-400 hover:text-white"
          aria-label="Close edge popover"
        >
          &times;
        </button>
      </div>

      <div className="py-2 space-y-1 font-mono text-[11px]">
        <div className="flex justify-between">
          <span className="text-slate-400">Source:</span>
          <span className="truncate max-w-[150px]">{sourceId}</span>
        </div>
        <div className="flex justify-between">
          <span className="text-slate-400">Target:</span>
          <span className="truncate max-w-[150px]">{targetId}</span>
        </div>
        <div className="flex justify-between">
          <span className="text-slate-400">Type:</span>
          <span className="text-blue-400">{relationshipType}</span>
        </div>
        {observedAt && (
          <div className="flex justify-between">
            <span className="text-slate-400">Observed:</span>
            <span className="text-slate-400">{new Date(observedAt).toLocaleDateString()}</span>
          </div>
        )}
      </div>
    </div>
  );
}
