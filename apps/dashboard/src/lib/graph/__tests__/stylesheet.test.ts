import { describe, expect, it } from "vitest";
import { getCytoscapeStylesheet } from "../stylesheet";

describe("cytoscape stylesheet", () => {
  it("returns stylesheet array containing node, edge, and state selectors", () => {
    const sheet = getCytoscapeStylesheet();
    expect(Array.isArray(sheet)).toBe(true);

    const selectors = sheet.map((s) => s.selector);
    expect(selectors).toContain("node");
    expect(selectors).toContain("edge");
    expect(selectors).toContain("node[band = 'critical']");
    expect(selectors).toContain("node:selected");
    expect(selectors).toContain("node.highlighted");
    expect(selectors).toContain("node.dimmed");
    expect(selectors).toContain("edge.highlighted");
  });

  it("configures bezier curves with arrows for directed edges", () => {
    const sheet = getCytoscapeStylesheet();
    const edgeRule = sheet.find((s) => s.selector === "edge");
    const style = edgeRule?.style as any;
    expect(style?.["curve-style"]).toBe("bezier");
    expect(style?.["target-arrow-shape"]).toBe("triangle");
  });
});
