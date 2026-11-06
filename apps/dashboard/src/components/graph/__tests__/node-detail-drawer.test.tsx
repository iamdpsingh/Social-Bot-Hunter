import { fireEvent, render, screen } from "@testing-library/react";
import React from "react";
import { describe, expect, it, vi } from "vitest";
import { NodeDetailDrawer } from "../node-detail-drawer";

describe("NodeDetailDrawer component", () => {
  const sampleNode = {
    id: "acc_42",
    label: "SuspiciousAlpha",
    score: 0.92,
    band: "critical",
    cluster_id: "cluster_1",
  };

  it("renders node metadata, risk score, and profile link", () => {
    const onClose = vi.fn();
    const onExpand = vi.fn();

    render(
      <NodeDetailDrawer
        scanId="s_100"
        nodeData={sampleNode}
        onClose={onClose}
        onExpandNeighbors={onExpand}
      />
    );

    expect(screen.getByText("SuspiciousAlpha")).toBeInTheDocument();
    expect(screen.getByText("92%")).toBeInTheDocument();
    expect(screen.getByText("cluster_1")).toBeInTheDocument();

    fireEvent.click(screen.getByRole("button", { name: "Expand Neighbors" }));
    expect(onExpand).toHaveBeenCalledWith("both");

    fireEvent.click(screen.getByRole("button", { name: "Close drawer" }));
    expect(onClose).toHaveBeenCalledTimes(1);
  });

  it("returns null when nodeData is null", () => {
    const { container } = render(
      <NodeDetailDrawer scanId="s_100" nodeData={null} onClose={vi.fn()} />
    );
    expect(container.firstChild).toBeNull();
  });
});
