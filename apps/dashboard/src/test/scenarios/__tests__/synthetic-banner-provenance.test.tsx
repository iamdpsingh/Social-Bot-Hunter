import React from "react";
import { describe, it, expect } from "vitest";
import { render, screen } from "@testing-library/react";
import { SyntheticDataBanner } from "../../../components/ui/synthetic-banner";

describe("Scenario: Synthetic Banner Provenance Disclosure", () => {
  it("renders prominent disclaimer banner with provenance metadata", () => {
    render(<SyntheticDataBanner />);
    expect(screen.getByText(/Synthetic Demo Data/i)).toBeInTheDocument();
    expect(screen.getByText(/Do not treat risk scores as empirical accusations/i)).toBeInTheDocument();
    expect(screen.getByText(/PROVENANCE: SYNTHETIC/i)).toBeInTheDocument();
  });
});
