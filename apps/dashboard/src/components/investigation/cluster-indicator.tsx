"use client";

import React from "react";
import { Share2 } from "lucide-react";

export interface ClusterIndicatorProps {
  clusterId?: string;
  clusterSize?: number;
  confidence?: number;
}

export function ClusterIndicator({ clusterId, clusterSize, confidence }: ClusterIndicatorProps) {
  if (!clusterId) {
    return (
      <span className="inline-flex items-center gap-1 text-[11px] text-muted-foreground">
        Standalone
      </span>
    );
  }

  return (
    <div
      className="inline-flex items-center gap-1.5 px-2 py-0.5 rounded-full text-xs font-medium bg-purple-500/10 text-purple-400 border border-purple-500/20"
      title={`Part of coordinated bot cluster ${clusterId}`}
      data-testid="cluster-indicator"
    >
      <Share2 className="h-3 w-3 shrink-0" />
      <span>Cluster #{clusterId.slice(-4)}</span>
      {clusterSize !== undefined && (
        <span className="text-[10px] bg-purple-500/20 px-1 rounded">{clusterSize} accts</span>
      )}
    </div>
  );
}
