import { render, screen } from "@testing-library/react";
import React from "react";
import { describe, expect, it } from "vitest";
import { CytoscapeCanvas } from "../cytoscape-canvas";

describe("CytoscapeCanvas component", () => {
  const sampleElements = {
    nodes: [{ data: { id: "n1", label: "Node 1" } }],
    edges: [],
  };

  it("renders container element with test id and accessible role", () => {
    render(<CytoscapeCanvas elements={sampleElements} />);
    const canvas = screen.getByTestId("cytoscape-canvas");
    expect(canvas).toBeInTheDocument();
    expect(canvas).toHaveAttribute("role", "region");
    expect(canvas).toHaveAttribute("aria-label", "Interactive directed graph canvas");
  });
});
