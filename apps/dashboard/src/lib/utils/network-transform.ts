export interface GraphNode {
  id: string;
  label: string;
  platform: string;
  riskScore: number;
}

export interface GraphEdge {
  source: string;
  target: string;
  relationshipType: string;
}

export function transformToGraphElements(
  nodes: GraphNode[],
  edges: GraphEdge[]
) {
  return [
    ...nodes.map((n) => ({
      data: {
        id: n.id,
        label: n.label,
        platform: n.platform,
        riskScore: n.riskScore,
      },
    })),
    ...edges.map((e, idx) => ({
      data: {
        id: `e_${idx}`,
        source: e.source,
        target: e.target,
        type: e.relationshipType,
      },
    })),
  ];
}
