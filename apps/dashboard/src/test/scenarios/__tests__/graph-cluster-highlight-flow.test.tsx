import { fireEvent, render, screen } from "@testing-library/react";
import React from "react";
import { describe, expect, it, vi } from "vitest";
import { ClusterSummaryBar } from "../../../components/graph/cluster-summary-bar";

describe("Scenario: Analyst filters graph by coordinated bot cluster", () => {
  const clusters = [
    { id: "sybil_swarm_1", method: "wcc", member_count: 12, confidence: "high", signal_strength: "strong", members: [] },
  ];

  it("selects cluster pill and allows clearing filter", () => {
    const onSelect = vi.fn();
    const onClear = vi.fn();

    const { rerender } = render(
      <ClusterSummaryBar
        clusters={clusters}
        activeClusterId=""
        onSelectCluster={onSelect}
        onClearCluster={onClear}
      />
    );

    fireEvent.click(screen.getByText("sybil_swarm_1"));
    expect(onSelect).toHaveBeenCalledWith("sybil_swarm_1");

    rerender(
      <ClusterSummaryBar
        clusters={clusters}
        activeClusterId="sybil_swarm_1"
        onSelectCluster={onSelect}
        onClearCluster={onClear}
      />
    );

    expect(screen.getByText("Clear filter")).toBeInTheDocument();
    fireEvent.click(screen.getByText("Clear filter"));
    expect(onClear).toHaveBeenCalledTimes(1);
  });
});
