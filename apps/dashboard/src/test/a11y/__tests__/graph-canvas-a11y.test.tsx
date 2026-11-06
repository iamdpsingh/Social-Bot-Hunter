import { render, screen } from "@testing-library/react";
import React from "react";
import { describe, expect, it } from "vitest";
import { CytoscapeCanvas } from "../../../components/graph/cytoscape-canvas";

describe("CytoscapeCanvas accessibility", () => {
  it("provides region role and informative aria-label", () => {
    render(<CytoscapeCanvas elements={{ nodes: [], edges: [] }} />);
    const region = screen.getByRole("region");
    expect(region).toHaveAttribute("aria-label", "Interactive directed graph canvas");
  });
});
