import { render, screen, fireEvent } from "@testing-library/react";
import { describe, it, expect, vi } from "vitest";
import { DiffClient } from "../../../app/history/diff/diff-client";
import * as diffHook from "../../../lib/hooks/use-scan-diff";

describe("Scenario: Multi-Scan Comparison Workflow", () => {
  it("renders side-by-side comparison with confirmed additions and score migrations", () => {
    vi.spyOn(diffHook, "useScanDiff").mockReturnValue({
      diff: {
        scan_a_id: "scan_a",
        scan_b_id: "scan_b",
        scan_a_platform: "x",
        scan_b_platform: "x",
        total_accounts_a: 50,
        total_accounts_b: 65,
        confirmed_additions_count: 15,
        coverage_gap_additions_count: 2,
        confirmed_removals_count: 3,
        coverage_gap_removals_count: 1,
        persisting_count: 47,
        escalated_risk_count: 6,
        deescalated_risk_count: 2,
        accounts: [
          {
            account_id: "bot_infiltrator",
            handle: "bot_infiltrator",
            status: "confirmed_added",
            risk_score_a: null,
            risk_score_b: 0.95,
            risk_band_a: null,
            risk_band_b: "critical",
            provenance_note: "Discovered in scan B; confirmed absent earlier",
          },
        ],
        risk_migrations: [],
        edge_diff_summary: {},
      },
      isLoading: false,
      isError: false,
      error: null,
    });

    render(<DiffClient />);

    expect(screen.getByTestId("diff-metric-summary")).toBeInTheDocument();
    expect(screen.getByText("15")).toBeInTheDocument();
    expect(screen.getByTestId("coverage-gap-banner")).toBeInTheDocument();
    expect(screen.getByText("@bot_infiltrator")).toBeInTheDocument();
  });
});
