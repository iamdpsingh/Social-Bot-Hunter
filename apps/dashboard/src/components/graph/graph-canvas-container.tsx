"use client";

import React, { useMemo, useState } from "react";
import type { Core } from "cytoscape";
import type { CytoscapeGraphElements, CytoscapeNodeData } from "../../lib/api/types";
import { filterCytoscapeElements } from "../../lib/graph/transform";
import { highlightNodeAndNeighbors } from "../../lib/graph/highlight";
import { exportGraphJson, exportGraphPng } from "../../lib/graph/export";
import type { LayoutPresetId } from "../../tokens/graph";
import { CytoscapeCanvas } from "./cytoscape-canvas";
import { GraphToolbar } from "./graph-toolbar";
import { GraphFilterPanel } from "./graph-filter-panel";
import { NodeDetailDrawer } from "./node-detail-drawer";
import { GraphLegend } from "./graph-legend";
import { GraphStatsChip } from "./graph-stats-chip";
import { GraphExportMenu } from "./graph-export-menu";
import { GraphEmptyState } from "./graph-empty-state";

export interface GraphCanvasContainerProps {
  scanId: string;
  initialElements: CytoscapeGraphElements;
  onExpandNode?: (nodeId: string, direction: "in" | "out" | "both") => void;
}

export function GraphCanvasContainer({
  scanId,
  initialElements,
  onExpandNode,
}: GraphCanvasContainerProps) {
  const [layoutPreset, setLayoutPreset] = useState<LayoutPresetId>("cose");
  const [searchQuery, setSearchQuery] = useState("");
  const [selectedBand, setSelectedBand] = useState("");
  const [minScore, setMinScore] = useState(0);
  const [clusterFilter, setClusterFilter] = useState("");
  const [selectedNode, setSelectedNode] = useState<CytoscapeNodeData | null>(null);
  const [cyInstance, setCyInstance] = useState<Core | null>(null);

  const filteredElements = useMemo(() => {
    return filterCytoscapeElements(initialElements, {
      query: searchQuery,
      riskBand: selectedBand || undefined,
      minScore: minScore > 0 ? minScore : undefined,
      clusterId: clusterFilter || undefined,
    });
  }, [initialElements, searchQuery, selectedBand, minScore, clusterFilter]);

  const handleSelectNode = (nodeId: string | null, nodeData?: CytoscapeNodeData | null) => {
    setSelectedNode(nodeData || null);
    if (cyInstance) {
      highlightNodeAndNeighbors(cyInstance, nodeId);
    }
  };

  const handleClearFilters = () => {
    setSearchQuery("");
    setSelectedBand("");
    setMinScore(0);
    setClusterFilter("");
  };

  return (
    <div data-testid="graph-canvas-container" className="flex flex-col gap-3 w-full">
      <div className="flex flex-wrap items-center justify-between gap-2">
        <GraphToolbar
          layoutPreset={layoutPreset}
          onChangeLayout={setLayoutPreset}
          onZoomIn={() => cyInstance?.zoom(cyInstance.zoom() * 1.25)}
          onZoomOut={() => cyInstance?.zoom(cyInstance.zoom() * 0.8)}
          onFit={() => cyInstance?.fit(undefined, 40)}
          onReset={() => {
            cyInstance?.reset();
            cyInstance?.fit(undefined, 40);
          }}
        />
        <div className="flex items-center gap-2">
          <GraphStatsChip
            nodeCount={filteredElements.nodes.length}
            edgeCount={filteredElements.edges.length}
          />
          <GraphExportMenu
            onExportPng={() => cyInstance && exportGraphPng(cyInstance)}
            onExportJson={() => cyInstance && exportGraphJson(cyInstance)}
          />
        </div>
      </div>

      <GraphFilterPanel
        searchQuery={searchQuery}
        onSearchChange={setSearchQuery}
        selectedBand={selectedBand}
        onBandChange={setSelectedBand}
        minScore={minScore}
        onMinScoreChange={setMinScore}
        clusterFilter={clusterFilter}
        onClusterChange={setClusterFilter}
        totalNodes={initialElements.nodes.length}
        filteredNodes={filteredElements.nodes.length}
        onClearFilters={handleClearFilters}
      />

      <div className="relative min-h-[500px] w-full">
        {filteredElements.nodes.length === 0 ? (
          <GraphEmptyState onResetFilters={handleClearFilters} />
        ) : (
          <CytoscapeCanvas
            elements={filteredElements}
            layoutPreset={layoutPreset}
            selectedNodeId={selectedNode?.id}
            onSelectNode={handleSelectNode}
            onInitCy={setCyInstance}
          />
        )}

        <NodeDetailDrawer
          scanId={scanId}
          nodeData={selectedNode}
          onClose={() => handleSelectNode(null, null)}
          onExpandNeighbors={(dir) => selectedNode && onExpandNode?.(selectedNode.id, dir)}
        />
      </div>

      <div className="flex justify-between items-center">
        <GraphLegend />
      </div>
    </div>
  );
}
