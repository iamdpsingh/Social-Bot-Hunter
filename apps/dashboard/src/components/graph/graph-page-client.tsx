"use client";

import React, { useState } from "react";
import { useGraphElements } from "../../lib/hooks/use-graph-elements";
import { useGraphClusters } from "../../lib/hooks/use-graph-clusters";
import { useGraphMetrics } from "../../lib/hooks/use-graph-metrics";
import { GraphBreadcrumbs } from "./graph-breadcrumbs";
import { GraphCanvasContainer } from "./graph-canvas-container";
import { AccessibleGraphTable } from "./accessible-graph-table";
import { ViewModeToggle, type GraphViewMode } from "./view-mode-toggle";
import { GraphMetricsCard } from "./graph-metrics-card";
import { ClusterSummaryBar } from "./cluster-summary-bar";
import { GraphScaleAlert } from "./graph-scale-alert";
import { GraphLoadingSkeleton } from "./graph-loading-skeleton";

export interface GraphPageClientProps {
  scanId: string;
}

export function GraphPageClient({ scanId }: GraphPageClientProps) {
  const [viewMode, setViewMode] = useState<GraphViewMode>("canvas");
  const [activeCluster, setActiveCluster] = useState<string>("");

  const { data: graphData, loading: loadingGraph } = useGraphElements(scanId, {
    maxNodes: 1000,
    clusterId: activeCluster || undefined,
  });
  const { clusters } = useGraphClusters(scanId);
  const { metrics, loading: loadingMetrics } = useGraphMetrics(scanId);

  const elements = graphData?.elements || { nodes: [], edges: [] };
  const nodeCount = elements.nodes.length;

  return (
    <div data-testid="graph-page-client" className="space-y-4 max-w-7xl mx-auto p-4 sm:p-6">
      <div className="flex flex-wrap items-center justify-between gap-3">
        <GraphBreadcrumbs scanId={scanId} />
        <ViewModeToggle viewMode={viewMode} onViewModeChange={setViewMode} />
      </div>

      <GraphMetricsCard metrics={metrics} loading={loadingMetrics} />

      <ClusterSummaryBar
        clusters={clusters}
        activeClusterId={activeCluster}
        onSelectCluster={setActiveCluster}
        onClearCluster={() => setActiveCluster("")}
      />

      <GraphScaleAlert nodeCount={nodeCount} onSwitchToTable={() => setViewMode("table")} />

      {loadingGraph ? (
        <GraphLoadingSkeleton />
      ) : viewMode === "canvas" ? (
        <GraphCanvasContainer scanId={scanId} initialElements={elements} />
      ) : (
        <AccessibleGraphTable scanId={scanId} elements={elements} />
      )}
    </div>
  );
}
