"use client";

import Link from "next/link";
import React from "react";
import type { CytoscapeNodeData } from "../../lib/api/types";
import { GRAPH_NODE_COLORS } from "../../tokens/graph";

export interface NodeDetailDrawerProps {
  scanId: string;
  nodeData: CytoscapeNodeData | null;
  onClose: () => void;
  onExpandNeighbors?: (direction: "in" | "out" | "both") => void;
}

export function NodeDetailDrawer({
  scanId,
  nodeData,
  onClose,
  onExpandNeighbors,
}: NodeDetailDrawerProps) {
  if (!nodeData) return null;

  const band = nodeData.band || "insufficient_evidence";
  const colors = GRAPH_NODE_COLORS[band] || GRAPH_NODE_COLORS.insufficient_evidence;
  const scorePercent = nodeData.score != null ? Math.round(nodeData.score * 100) : null;

  return (
    <div
      data-testid="node-detail-drawer"
      className="absolute top-4 right-4 z-20 w-80 bg-slate-900 border border-slate-700/80 rounded-xl shadow-2xl p-4 text-slate-200 backdrop-blur-md"
      role="complementary"
      aria-label="Account details side panel"
    >
      <div className="flex items-start justify-between pb-3 border-b border-slate-800">
        <div>
          <h3 className="font-semibold text-sm truncate max-w-[200px]" title={nodeData.label || nodeData.id}>
            {nodeData.label || nodeData.id}
          </h3>
          <p className="text-xs text-slate-400 font-mono truncate">{nodeData.id}</p>
        </div>
        <button
          type="button"
          onClick={onClose}
          className="text-slate-400 hover:text-slate-200 text-lg leading-none p-1 rounded hover:bg-slate-800"
          aria-label="Close drawer"
        >
          &times;
        </button>
      </div>

      <div className="py-3 space-y-3">
        <div className="flex items-center justify-between">
          <span className="text-xs text-slate-400">Risk Score</span>
          <div className="flex items-center gap-2">
            <span
              className="inline-block w-2.5 h-2.5 rounded-full"
              style={{ backgroundColor: colors.bg }}
              aria-hidden="true"
            />
            <span className="font-bold text-sm">
              {scorePercent !== null ? `${scorePercent}%` : "Unscored"}
            </span>
          </div>
        </div>

        <div className="flex items-center justify-between text-xs">
          <span className="text-slate-400">Classification</span>
          <span
            className="px-2 py-0.5 rounded font-medium text-xs capitalize"
            style={{ backgroundColor: `${colors.bg}22`, color: colors.bg, border: `1px solid ${colors.border}55` }}
          >
            {band.replace("_", " ")}
          </span>
        </div>

        {nodeData.cluster_id && (
          <div className="flex items-center justify-between text-xs">
            <span className="text-slate-400">Cluster</span>
            <span className="px-2 py-0.5 rounded bg-purple-900/40 text-purple-300 border border-purple-700/50 font-mono">
              {nodeData.cluster_id}
            </span>
          </div>
        )}
      </div>

      <div className="pt-3 border-t border-slate-800 space-y-2">
        {onExpandNeighbors && (
          <div className="flex gap-1.5">
            <button
              type="button"
              onClick={() => onExpandNeighbors("both")}
              className="flex-1 px-2.5 py-1.5 text-xs font-medium rounded bg-blue-600 hover:bg-blue-500 text-white transition"
            >
              Expand Neighbors
            </button>
          </div>
        )}

        <Link
          href={`/investigations/${scanId}/accounts/${nodeData.id}`}
          className="block w-full text-center px-2.5 py-1.5 text-xs font-medium rounded bg-slate-800 hover:bg-slate-700 text-slate-200 transition"
        >
          View Full Account Profile &rarr;
        </Link>
      </div>
    </div>
  );
}
