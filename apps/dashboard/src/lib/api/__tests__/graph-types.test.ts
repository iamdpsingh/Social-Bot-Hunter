import { describe, expect, it } from "vitest";
import type {
  CytoscapeGraphResponse,
  GraphExportBundleResponse,
  GraphMetricsResponse,
  NodeNeighborsResponse,
} from "../types";

describe("graph api types contract", () => {
  it("validates CytoscapeGraphResponse structural type assignment", () => {
    const res: CytoscapeGraphResponse = {
      scan_id: "s_123",
      elements: {
        nodes: [{ data: { id: "node_1", score: 0.95, band: "critical" } }],
        edges: [{ data: { id: "node_1->node_2", source: "node_1", target: "node_2" } }],
      },
      node_count: 1,
      edge_count: 1,
    };
    expect(res.scan_id).toBe("s_123");
    expect(res.elements.nodes).toHaveLength(1);
  });

  it("validates NodeNeighborsResponse and GraphMetricsResponse structures", () => {
    const neighbors: NodeNeighborsResponse = {
      scan_id: "s_1",
      center_node_id: "focal",
      direction: "both",
      radius: 1,
      neighbors: [
        {
          node_id: "peer_1",
          direction: "inbound",
          relationship_type: "follower",
          risk_score: 0.82,
          risk_band: "high",
        },
      ],
      total: 1,
    };
    expect(neighbors.neighbors[0].risk_band).toBe("high");

    const metrics: GraphMetricsResponse = {
      scan_id: "s_1",
      node_count: 50,
      edge_count: 120,
      density: 0.048,
      reciprocity: 0.22,
      weakly_connected_components: 2,
      strongly_connected_components: 12,
      avg_in_degree: 2.4,
      avg_out_degree: 2.4,
    };
    expect(metrics.density).toBe(0.048);
  });
});
