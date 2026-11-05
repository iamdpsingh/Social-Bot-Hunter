import React from "react";
import { describe, it, expect } from "vitest";
import { render, screen } from "@testing-library/react";
import { OverviewSummaryCard } from "../overview-summary-card";

describe("OverviewSummaryCard", () => {
  it("renders calculated bot ratio, counts, and critical badges", () => {
    render(
      <OverviewSummaryCard
        totalAccounts={200}
        botAccounts={50}
        avgRiskScore={0.72}
        criticalCount={14}
      />
    );

    expect(screen.getByText("200")).toBeInTheDocument();
    expect(screen.getByText("50")).toBeInTheDocument();
    expect(screen.getByText("25.0% flag rate")).toBeInTheDocument();
    expect(screen.getByText("0.72")).toBeInTheDocument();
    expect(screen.getByText("14")).toBeInTheDocument();
  });
});
