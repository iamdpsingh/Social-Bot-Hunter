import { render, screen } from "@testing-library/react";
import { describe, it, expect } from "vitest";
import { DiffMetricSummary } from "../diff-metric-summary";

describe("DiffMetricSummary", () => {
  const mockDiff = {
    scan_a_id: "s1",
    scan_b_id: "s2",
    scan_a_platform: "x",
    scan_b_platform: "x",
    total_accounts_a: 10,
    total_accounts_b: 12,
    confirmed_additions_count: 3,
    coverage_gap_additions_count: 1,
    confirmed_removals_count: 2,
    coverage_gap_removals_count: 0,
    persisting_count: 8,
    escalated_risk_count: 4,
    deescalated_risk_count: 1,
    accounts: [],
    risk_migrations: [],
    edge_diff_summary: {},
  };

  it("renders metric cards accurately", () => {
    render(<DiffMetricSummary diff={mockDiff} />);
    expect(screen.getByTestId("diff-metric-summary")).toBeInTheDocument();
    expect(screen.getByText("Confirmed Added")).toBeInTheDocument();
    expect(screen.getByText("Confirmed Removed")).toBeInTheDocument();
    expect(screen.getByText("3")).toBeInTheDocument();
  });
});
