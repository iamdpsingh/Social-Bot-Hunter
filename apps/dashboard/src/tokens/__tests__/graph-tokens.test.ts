import { describe, expect, it } from "vitest";
import {
  CLUSTER_HULL_PALETTE,
  GRAPH_EDGE_COLORS,
  GRAPH_NODE_COLORS,
  GRAPH_NODE_SIZES,
  LAYOUT_PRESETS,
} from "../graph";

describe("graph tokens", () => {
  it("defines node colors for all five risk bands", () => {
    expect(GRAPH_NODE_COLORS.critical.bg).toBe("#ef4444");
    expect(GRAPH_NODE_COLORS.high.bg).toBe("#f97316");
    expect(GRAPH_NODE_COLORS.medium.bg).toBe("#eab308");
    expect(GRAPH_NODE_COLORS.low.bg).toBe("#22c55e");
    expect(GRAPH_NODE_COLORS.insufficient_evidence.bg).toBe("#94a3b8");
  });

  it("defines standard node sizes including focal node", () => {
    expect(GRAPH_NODE_SIZES.sm).toBe(24);
    expect(GRAPH_NODE_SIZES.focal).toBe(50);
  });

  it("exports 5 layout presets", () => {
    expect(LAYOUT_PRESETS).toHaveLength(5);
    expect(LAYOUT_PRESETS.map((p) => p.id)).toContain("cose");
    expect(LAYOUT_PRESETS.map((p) => p.id)).toContain("concentric");
  });

  it("defines at least 5 cluster hull colors", () => {
    expect(CLUSTER_HULL_PALETTE.length).toBeGreaterThanOrEqual(5);
  });
});
