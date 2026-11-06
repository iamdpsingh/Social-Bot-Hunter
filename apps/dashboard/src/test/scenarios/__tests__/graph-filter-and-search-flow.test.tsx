import { fireEvent, render, screen } from "@testing-library/react";
import React from "react";
import { describe, expect, it } from "vitest";
import { GraphCanvasContainer } from "../../../components/graph/graph-canvas-container";

describe("Scenario: Analyst filters nodes by search query and score threshold", () => {
  const elements = {
    nodes: [
      { data: { id: "alpha_bot", label: "Alpha Bot", score: 0.85, band: "critical" } },
      { data: { id: "casual_user", label: "Casual User", score: 0.15, band: "low" } },
    ],
    edges: [],
  };

  it("filters graph elements dynamically via search box", () => {
    render(<GraphCanvasContainer scanId="s1" initialElements={elements} />);

    const searchInput = screen.getByLabelText("Search graph accounts");
    fireEvent.change(searchInput, { target: { value: "casual" } });

    // Expect node counter to update to 1 node
    expect(screen.getByTestId("graph-filter-panel")).toHaveTextContent("Showing 1 / 2");
  });
});
