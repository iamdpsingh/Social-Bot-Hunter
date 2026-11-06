import { fireEvent, render, screen } from "@testing-library/react";
import React from "react";
import { describe, expect, it, vi } from "vitest";
import { ClusterSummaryBar } from "../cluster-summary-bar";

describe("ClusterSummaryBar component", () => {
  const sampleClusters = [
    { id: "cluster_1", method: "wcc", member_count: 8, confidence: "high", signal_strength: "strong", members: [] },
    { id: "cluster_2", method: "wcc", member_count: 4, confidence: "medium", signal_strength: "moderate", members: [] },
  ];

  it("renders cluster pill badges with counts", () => {
    const onSelect = vi.fn();
    const onClear = vi.fn();

    render(
      <ClusterSummaryBar
        clusters={sampleClusters}
        activeClusterId="cluster_1"
        onSelectCluster={onSelect}
        onClearCluster={onClear}
      />
    );

    expect(screen.getByText("cluster_1")).toBeInTheDocument();
    expect(screen.getByText("8 bots")).toBeInTheDocument();

    fireEvent.click(screen.getByText("cluster_2"));
    expect(onSelect).toHaveBeenCalledWith("cluster_2");

    fireEvent.click(screen.getByText("Clear filter"));
    expect(onClear).toHaveBeenCalledTimes(1);
  });
});
