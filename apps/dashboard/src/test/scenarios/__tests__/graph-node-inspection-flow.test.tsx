import { fireEvent, render, screen } from "@testing-library/react";
import React from "react";
import { describe, expect, it } from "vitest";
import { AccessibleGraphTable } from "../../../components/graph/accessible-graph-table";

describe("Scenario: Analyst inspects node details from table alternative", () => {
  const elements = {
    nodes: [
      { data: { id: "target_bot", label: "BotClusterHub", score: 0.94, band: "critical", cluster_id: "botnet_x" } },
    ],
    edges: [],
  };

  it("displays node risk classification, score, and link to account investigation", () => {
    render(<AccessibleGraphTable scanId="scan_gamma" elements={elements} />);

    expect(screen.getByText("BotClusterHub")).toBeInTheDocument();
    expect(screen.getByText("94%")).toBeInTheDocument();
    expect(screen.getByText("botnet_x")).toBeInTheDocument();

    const link = screen.getByRole("link", { name: "Profile →" });
    expect(link).toHaveAttribute("href", "/investigations/scan_gamma/accounts/target_bot");
  });
});
