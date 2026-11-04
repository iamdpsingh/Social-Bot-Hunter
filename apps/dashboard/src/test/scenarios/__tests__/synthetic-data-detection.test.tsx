import React from "react";
import { describe, it, expect } from "vitest";
import { render, screen } from "@testing-library/react";
import { SyntheticDataBanner } from "../../../components/ui/synthetic-banner";
import { isSyntheticObservation } from "../../../lib/utils/provenance";

describe("Scenario: Synthetic Data Provenance Disclosure", () => {
  it("detects synthetic data flag and displays synthetic warning banner", () => {
    const testRecord = { is_synthetic: true, target: "bot_army_01" };
    expect(isSyntheticObservation(testRecord)).toBe(true);

    render(<SyntheticDataBanner />);
    expect(screen.getByText("Synthetic Demo Data")).toBeInTheDocument();
    expect(screen.getByText("PROVENANCE: SYNTHETIC")).toBeInTheDocument();
  });
});
