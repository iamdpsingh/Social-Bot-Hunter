import React from "react";
import { describe, it, expect } from "vitest";
import { render, screen } from "@testing-library/react";
import { AccountNeighborhoodViewer } from "../../../components/investigation/account-neighborhood-viewer";

describe("Scenario: Account Neighborhood Inspection", () => {
  it("renders incoming and outgoing 1-hop connections with truncated labels", () => {
    const inEdges = [
      { source: "suspicious_cluster_node_1", target: "target", relationship_type: "follower" },
    ];
    const outEdges = [
      { source: "target", target: "amplified_anchor_account", relationship_type: "following" },
    ];

    render(<AccountNeighborhoodViewer inEdges={inEdges} outEdges={outEdges} />);
    expect(screen.getByText("suspicious_cluster_node_1")).toBeInTheDocument();
    expect(screen.getByText("amplified_anchor_account")).toBeInTheDocument();
  });
});
