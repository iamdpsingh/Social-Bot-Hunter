import { describe, expect, it } from "vitest";
import { getLayoutOptions } from "../layouts";

describe("cytoscape layouts", () => {
  it("returns cose force-directed configuration", () => {
    const layout = getLayoutOptions("cose");
    expect(layout.name).toBe("cose");
    expect(layout.animate).toBe(true);
  });

  it("returns concentric layout with risk score weighting", () => {
    const layout = getLayoutOptions("concentric") as any;
    expect(layout.name).toBe("concentric");
    expect(typeof layout.concentric).toBe("function");

    // mock node with score 0.8
    const mockNodeHigh = { data: (k: string) => (k === "score" ? 0.8 : undefined) };
    expect(layout.concentric(mockNodeHigh)).toBe(8);

    // mock node with critical band
    const mockNodeCrit = { data: (k: string) => (k === "band" ? "critical" : undefined) };
    expect(layout.concentric(mockNodeCrit)).toBe(10);
  });

  it("returns circle, breadthfirst, and grid layout presets", () => {
    expect(getLayoutOptions("circle").name).toBe("circle");
    expect(getLayoutOptions("breadthfirst").name).toBe("breadthfirst");
    expect(getLayoutOptions("grid").name).toBe("grid");
  });
});
