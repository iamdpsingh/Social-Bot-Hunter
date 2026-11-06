import { render, screen } from "@testing-library/react";
import React from "react";
import { describe, expect, it } from "vitest";
import { GraphCanvasContainer } from "../graph-canvas-container";

describe("GraphCanvasContainer component", () => {
  const sampleElements = {
    nodes: [
      { data: { id: "a", label: "Alpha", score: 0.9, band: "critical" } },
      { data: { id: "b", label: "Beta", score: 0.2, band: "low" } },
    ],
    edges: [{ data: { id: "a->b", source: "a", target: "b" } }],
  };

  it("renders container including toolbar, filter panel, and stats chip", () => {
    render(<GraphCanvasContainer scanId="scan_1" initialElements={sampleElements} />);
    expect(screen.getByTestId("graph-canvas-container")).toBeInTheDocument();
    expect(screen.getByTestId("graph-toolbar")).toBeInTheDocument();
    expect(screen.getByTestId("graph-filter-panel")).toBeInTheDocument();
    expect(screen.getByTestId("graph-stats-chip")).toBeInTheDocument();
  });
});
