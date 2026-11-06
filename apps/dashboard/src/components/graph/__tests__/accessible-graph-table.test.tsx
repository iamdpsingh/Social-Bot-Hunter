import { fireEvent, render, screen } from "@testing-library/react";
import React from "react";
import { describe, expect, it, vi } from "vitest";
import { AccessibleGraphTable } from "../accessible-graph-table";

describe("AccessibleGraphTable component", () => {
  const elements = {
    nodes: [
      { data: { id: "bot_1", label: "Alpha", score: 0.9, band: "critical", cluster_id: "c1" } },
      { data: { id: "bot_2", label: "Beta", score: 0.2, band: "low" } },
    ],
    edges: [{ data: { id: "e1", source: "bot_1", target: "bot_2" } }],
  };

  it("renders table with sortable columns and node degrees", () => {
    const onSelect = vi.fn();
    render(<AccessibleGraphTable scanId="s1" elements={elements} onSelectNode={onSelect} />);

    expect(screen.getByText("Account / Node ID")).toBeInTheDocument();
    expect(screen.getByText("Alpha")).toBeInTheDocument();
    expect(screen.getByText("Beta")).toBeInTheDocument();
    expect(screen.getByText("90%")).toBeInTheDocument();
    expect(screen.getByText("c1")).toBeInTheDocument();

    fireEvent.click(screen.getByText("Alpha"));
    expect(onSelect).toHaveBeenCalledWith("bot_1");
  });
});
