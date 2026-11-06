"use client";

import React from "react";
import type { CytoscapeNodeData } from "../../lib/api/types";

export interface NodeHoverCardProps {
  nodeData: CytoscapeNodeData | null;
  position?: { x: number; y: number };
}

export function NodeHoverCard({ nodeData, position }: NodeHoverCardProps) {
  if (!nodeData) return null;

  const style = position
    ? { left: `${position.x + 12}px`, top: `${position.y + 12}px` }
    : undefined;

  return (
    <div
      data-testid="node-hover-card"
      style={style}
      className="absolute z-30 pointer-events-none bg-slate-900/95 border border-slate-700/80 px-2.5 py-1.5 rounded shadow-lg text-xs text-slate-200 backdrop-blur-sm"
      role="tooltip"
    >
      <p className="font-semibold">{nodeData.label || nodeData.id}</p>
      {nodeData.score != null && (
        <p className="text-[10px] text-slate-400">Score: {Math.round(nodeData.score * 100)}%</p>
      )}
    </div>
  );
}
