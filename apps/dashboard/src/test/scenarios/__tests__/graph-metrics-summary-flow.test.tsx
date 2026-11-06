import { render, screen } from "@testing-library/react";
import React from "react";
import { describe, expect, it } from "vitest";
import { GraphMetricsCard } from "../../../components/graph/graph-metrics-card";

describe("Scenario: Analyst inspects macroscopic graph topology measures", () => {
  const metrics = {
    scan_id: "scan_top",
    node_count: 500,
    edge_count: 1250,
    density: 0.005,
    reciprocity: 0.28,
    weakly_connected_components: 2,
    strongly_connected_components: 18,
    avg_in_degree: 2.5,
    avg_out_degree: 2.5,
  };

  it("displays node count, edge density, and reciprocity metrics", () => {
    render(<GraphMetricsCard metrics={metrics} />);
    expect(screen.getByText("500")).toBeInTheDocument();
    expect(screen.getByText("1,250")).toBeInTheDocument();
    expect(screen.getByText("0.0050")).toBeInTheDocument();
    expect(screen.getByText("28.0%")).toBeInTheDocument();
  });
});
