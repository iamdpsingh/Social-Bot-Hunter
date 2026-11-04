import { render, screen } from "@testing-library/react";
import { describe, it, expect } from "vitest";
import React from "react";
import { SyntheticDataBanner } from "../synthetic-banner";

describe("SyntheticDataBanner component", () => {
  it("renders synthetic warning banner with accessibility role", () => {
    render(<SyntheticDataBanner />);
    const banner = screen.getByRole("status");
    expect(banner).toBeInTheDocument();
    expect(screen.getByText(/synthetic demo data/i)).toBeInTheDocument();
    expect(screen.getByText(/provenance: synthetic/i)).toBeInTheDocument();
  });

  it("renders custom subtext when provided", () => {
    render(<SyntheticDataBanner subtext="Custom provenance test notice" />);
    expect(screen.getByText("Custom provenance test notice")).toBeInTheDocument();
  });
});
