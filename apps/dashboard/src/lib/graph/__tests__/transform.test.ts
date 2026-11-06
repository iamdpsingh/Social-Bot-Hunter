import { describe, expect, it } from "vitest";
import type { CytoscapeGraphElements } from "../../api/types";
import { filterCytoscapeElements, getGraphSummaryStats } from "../transform";

describe("graph transform and filtering", () => {
  const sampleElements: CytoscapeGraphElements = {
    nodes: [
      { data: { id: "bot_1", label: "Alpha Bot", score: 0.95, band: "critical", cluster_id: "c_1" } },
      { data: { id: "bot_2", label: "Beta Bot", score: 0.72, band: "high", cluster_id: "c_1" } },
      { data: { id: "innocent", label: "Real User", score: 0.1, band: "low" } },
    ],
    edges: [
      { data: { id: "bot_1->bot_2", source: "bot_1", target: "bot_2" } },
      { data: { id: "bot_2->innocent", source: "bot_2", target: "innocent" } },
    ],
  };

  it("filters nodes by minimum score threshold and strips orphan edges", () => {
    const filtered = filterCytoscapeElements(sampleElements, { minScore: 0.7 });
    expect(filtered.nodes).toHaveLength(2);
    expect(filtered.edges).toHaveLength(1);
    expect(filtered.edges[0].data.id).toBe("bot_1->bot_2");
  });

  it("filters by cluster id", () => {
    const filtered = filterCytoscapeElements(sampleElements, { clusterId: "c_1" });
    expect(filtered.nodes).toHaveLength(2);
  });

  it("filters by text query on label or id", () => {
    const filtered = filterCytoscapeElements(sampleElements, { query: "alpha" });
    expect(filtered.nodes).toHaveLength(1);
    expect(filtered.nodes[0].data.id).toBe("bot_1");
  });

  it("computes summary stats including risk band distributions", () => {
    const stats = getGraphSummaryStats(sampleElements);
    expect(stats.nodeCount).toBe(3);
    expect(stats.edgeCount).toBe(2);
    expect(stats.bandCounts.critical).toBe(1);
    expect(stats.bandCounts.low).toBe(1);
  });
});
