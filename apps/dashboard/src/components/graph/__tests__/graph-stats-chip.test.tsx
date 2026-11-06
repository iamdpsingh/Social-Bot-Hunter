import { render, screen } from "@testing-library/react";
import React from "react";
import { describe, expect, it } from "vitest";
import { GraphStatsChip } from "../graph-stats-chip";

describe("GraphStatsChip component", () => {
  it("renders formatted nodes and edges count", () => {
    render(<GraphStatsChip nodeCount={150} edgeCount={320} />);
    expect(screen.getByText("150")).toBeInTheDocument();
    expect(screen.getByText("320")).toBeInTheDocument();
  });
});
