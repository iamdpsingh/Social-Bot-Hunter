import React from "react";
import { describe, it, expect } from "vitest";
import { render, screen } from "@testing-library/react";
import { RelationshipTable } from "../relationship-table";

describe("RelationshipTable component", () => {
  it("renders accounts rows with risk badges and inspect links", () => {
    const accounts: any[] = [
      {
        id: "1",
        platform_account_id: "x_101",
        username: "bot_army_01",
        score: 0.88,
        band: "critical",
        evidence_coverage: 0.9,
        features_available: 8,
        features_total: 10,
      },
    ];
    render(<RelationshipTable scanId="scan_10" accounts={accounts} />);
    expect(screen.getByText("@bot_army_01")).toBeInTheDocument();
    expect(screen.getByText("Critical Risk")).toBeInTheDocument();
    expect(screen.getByText("88%")).toBeInTheDocument();
    expect(screen.getByText("Inspect")).toBeInTheDocument();
  });
});
