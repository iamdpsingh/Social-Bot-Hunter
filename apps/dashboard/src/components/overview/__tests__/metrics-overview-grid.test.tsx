import React from "react";
import { describe, it, expect } from "vitest";
import { render, screen } from "@testing-library/react";
import { MetricsOverviewGrid } from "../metrics-overview-grid";

describe("MetricsOverviewGrid component", () => {
  it("renders 4 core investigation stat cards", () => {
    render(
      <MetricsOverviewGrid
        totalScans={42}
        activeInvestigations={3}
        flaggedAccountsRate={18.4}
        networkClustersDetected={7}
      />
    );

    expect(screen.getByText("Total Scans")).toBeInTheDocument();
    expect(screen.getByText("42")).toBeInTheDocument();
    expect(screen.getByText("Active Investigations")).toBeInTheDocument();
    expect(screen.getByText("3")).toBeInTheDocument();
    expect(screen.getByText("18.4%")).toBeInTheDocument();
    expect(screen.getByText("Coordinated Clusters")).toBeInTheDocument();
    expect(screen.getByText("7")).toBeInTheDocument();
  });
});
