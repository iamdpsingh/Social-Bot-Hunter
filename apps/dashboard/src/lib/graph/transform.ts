import type { CytoscapeGraphElements } from "../api/types";

export interface GraphFilterOptions {
  minScore?: number;
  riskBand?: string;
  clusterId?: string;
  query?: string;
}

export function filterCytoscapeElements(
  elements: CytoscapeGraphElements,
  filters: GraphFilterOptions
): CytoscapeGraphElements {
  const { minScore, riskBand, clusterId, query } = filters;
  const q = query?.trim().toLowerCase();

  const matchingNodes = elements.nodes.filter((n) => {
    const data = n.data;
    if (minScore !== undefined && data.score != null && data.score < minScore) {
      return false;
    }
    if (riskBand && data.band !== riskBand) {
      return false;
    }
    if (clusterId && data.cluster_id !== clusterId) {
      return false;
    }
    if (q) {
      const idMatch = data.id.toLowerCase().includes(q);
      const labelMatch = data.label ? data.label.toLowerCase().includes(q) : false;
      if (!idMatch && !labelMatch) return false;
    }
    return true;
  });

  const matchingNodeIds = new Set(matchingNodes.map((n) => n.data.id));

  const matchingEdges = elements.edges.filter((e) => {
    return matchingNodeIds.has(e.data.source) && matchingNodeIds.has(e.data.target);
  });

  return {
    nodes: matchingNodes,
    edges: matchingEdges,
  };
}

export function getGraphSummaryStats(elements: CytoscapeGraphElements) {
  const nodeCount = elements.nodes.length;
  const edgeCount = elements.edges.length;

  const bandCounts: Record<string, number> = {};
  elements.nodes.forEach((n) => {
    const band = n.data.band || "insufficient_evidence";
    bandCounts[band] = (bandCounts[band] || 0) + 1;
  });

  return {
    nodeCount,
    edgeCount,
    bandCounts,
  };
}
