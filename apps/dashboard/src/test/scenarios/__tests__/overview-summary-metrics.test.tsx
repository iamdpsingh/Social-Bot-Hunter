import React from "react";
import { describe, it, expect } from "vitest";
import { render, screen } from "@testing-library/react";
import { OverviewSummaryCard } from "../../../components/investigation/overview-summary-card";

describe("Scenario: Overview Summary Metric Aggregation", () => {
  it("calculates zero flag rate safely on empty total accounts", () => {
    render(<OverviewSummaryCard totalAccounts={0} botAccounts={0} avgRiskScore={0} criticalCount={0} />);
    expect(screen.getByText("0.0% flag rate")).toBeInTheDocument();
  });
});
