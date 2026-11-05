import React from "react";
import { describe, it, expect } from "vitest";
import { render, screen } from "@testing-library/react";
import { RelationshipTable } from "../../../components/investigation/relationship-table";

describe("Scenario: Account Investigation Routing", () => {
  it("renders inspect deep links pointing to target account detail page", () => {
    const accounts = [
      {
        id: "acc_99",
        platform_account_id: "target_user_99",
        username: "target_user_99",
        score: 0.94,
        band: "critical" as const,
        evidence_coverage: 1.0,
        features_available: 8,
        features_total: 8,
        scan_id: "scan_workspace_01",
        pid: "x_user",
        status: "scored" as const,
        contributions: [],
        limitations: [],
      },
    ];

    render(<RelationshipTable scanId="scan_workspace_01" accounts={accounts} />);
    const link = screen.getByRole("link", { name: /Inspect/i });
    expect(link).toHaveAttribute("href", "/investigations/scan_workspace_01/accounts/target_user_99");
  });
});
