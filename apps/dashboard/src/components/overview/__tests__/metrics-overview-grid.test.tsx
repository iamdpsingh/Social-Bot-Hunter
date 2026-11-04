import React from "react";
import { describe, it, expect, vi } from "vitest";
import { render, screen } from "@testing-library/react";
import { MetricsOverviewGrid } from "../metrics-overview-grid";

vi.mock("../../../lib/hooks/use-scans", () => ({
  useScans: () => ({
    scans: [
      { id: "1", status: "running" },
      { id: "2", status: "complete" },
    ],
    total: 2,
  }),
}));

describe("MetricsOverviewGrid component", () => {
  it("renders 4 core investigation stat cards", () => {
    render(<MetricsOverviewGrid />);
    expect(screen.getByText("Total Investigations")).toBeInTheDocument();
    expect(screen.getByText("Completed Scans")).toBeInTheDocument();
    expect(screen.getByText("Coordinated Clusters")).toBeInTheDocument();
    expect(screen.getByText("Failed / Cancelled")).toBeInTheDocument();
  });
});
