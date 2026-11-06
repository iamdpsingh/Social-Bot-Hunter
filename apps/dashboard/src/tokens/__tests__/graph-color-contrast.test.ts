import { describe, expect, it } from "vitest";
import { GRAPH_NODE_COLORS } from "../graph";

describe("graph node color contrast", () => {
  it("ensures all risk bands have valid hex background and text colors", () => {
    const bands = ["critical", "high", "medium", "low", "insufficient_evidence"];
    bands.forEach((b) => {
      const token = GRAPH_NODE_COLORS[b];
      expect(token.bg).toMatch(/^#[0-9a-fA-F]{6}$/);
      expect(token.text).toMatch(/^#[0-9a-fA-F]{6}$/);
    });
  });
});
