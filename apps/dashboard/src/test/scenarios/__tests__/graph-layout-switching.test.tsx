import { fireEvent, render, screen } from "@testing-library/react";
import React from "react";
import { describe, expect, it } from "vitest";
import { GraphCanvasContainer } from "../../../components/graph/graph-canvas-container";

describe("Scenario: User switches graph layout presets", () => {
  const elements = {
    nodes: [
      { data: { id: "a", label: "Alpha", score: 0.9, band: "critical" } },
      { data: { id: "b", label: "Beta", score: 0.4, band: "medium" } },
    ],
    edges: [{ data: { id: "a->b", source: "a", target: "b" } }],
  };

  it("updates layout selector to concentric and grid", () => {
    render(<GraphCanvasContainer scanId="s1" initialElements={elements} />);
    const select = screen.getByLabelText("Layout:");

    fireEvent.change(select, { target: { value: "concentric" } });
    expect((select as HTMLSelectElement).value).toBe("concentric");

    fireEvent.change(select, { target: { value: "grid" } });
    expect((select as HTMLSelectElement).value).toBe("grid");
  });
});
