import { render, screen } from "@testing-library/react";
import React from "react";
import { describe, expect, it } from "vitest";
import { GraphMetricsCard } from "../graph-metrics-card";

describe("GraphMetricsCard component", () => {
  const metrics = {
    scan_id: "s_1",
    node_count: 1420,
    edge_count: 3890,
    density: 0.0019,
    reciprocity: 0.124,
    weakly_connected_components: 4,
    strongly_connected_components: 28,
    avg_in_degree: 2.74,
    avg_out_degree: 2.74,
  };

  it("renders formatted node count, edges, density, and reciprocity", () => {
    render(<GraphMetricsCard metrics={metrics} />);
    expect(screen.getByText("1,420")).toBeInTheDocument();
    expect(screen.getByText("3,890")).toBeInTheDocument();
    expect(screen.getByText("0.0019")).toBeInTheDocument();
    expect(screen.getByText("12.4%")).toBeInTheDocument();
  });

  it("renders loading skeleton when loading is true", () => {
    render(<GraphMetricsCard metrics={null} loading={true} />);
    expect(screen.getByTestId("graph-metrics-card-loading")).toBeInTheDocument();
  });
});
