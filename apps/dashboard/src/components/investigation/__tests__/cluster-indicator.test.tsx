import React from "react";
import { describe, it, expect } from "vitest";
import { render, screen } from "@testing-library/react";
import { ClusterIndicator } from "../cluster-indicator";

describe("ClusterIndicator", () => {
  it("renders cluster pill with short hash and size when present", () => {
    render(<ClusterIndicator clusterId="cls_987654" clusterSize={12} confidence={0.92} />);
    expect(screen.getByTestId("cluster-indicator")).toBeInTheDocument();
    expect(screen.getByText("Cluster #7654")).toBeInTheDocument();
    expect(screen.getByText("12 accts")).toBeInTheDocument();
  });

  it("renders standalone fallback when clusterId is missing", () => {
    render(<ClusterIndicator />);
    expect(screen.getByText("Standalone")).toBeInTheDocument();
  });
});
