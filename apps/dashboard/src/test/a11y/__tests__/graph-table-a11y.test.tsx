import { render, screen } from "@testing-library/react";
import React from "react";
import { describe, expect, it } from "vitest";
import { AccessibleGraphTable } from "../../../components/graph/accessible-graph-table";

describe("AccessibleGraphTable accessibility", () => {
  const elements = {
    nodes: [{ data: { id: "acc_1", label: "AlphaBot", score: 0.9, band: "critical" } }],
    edges: [],
  };

  it("provides table headers with scope col and accessible table region", () => {
    render(<AccessibleGraphTable scanId="s1" elements={elements} />);
    const region = screen.getByRole("region", { name: "Accessible network accounts table" });
    expect(region).toBeInTheDocument();

    const headers = screen.getAllByRole("columnheader");
    expect(headers.length).toBeGreaterThanOrEqual(5);
    expect(headers[0]).toHaveAttribute("scope", "col");
  });
});
