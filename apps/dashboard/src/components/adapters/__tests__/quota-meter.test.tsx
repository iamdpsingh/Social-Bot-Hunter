import React from "react";
import { render, screen } from "@testing-library/react";
import { describe, it, expect } from "vitest";
import { QuotaMeter } from "../quota-meter";

describe("QuotaMeter", () => {
  it("renders normal quota progress bar cleanly", () => {
    render(<QuotaMeter platform="youtube" dailyLimit={10000} unitsUsed={2500} />);
    expect(screen.getByText(/2,500 \/ 10,000 units \(25%\)/i)).toBeInTheDocument();
    const bar = screen.getByRole("progressbar");
    expect(bar).toHaveAttribute("aria-valuenow", "25");
  });

  it("renders warning banner when quota exceeds 80%", () => {
    render(<QuotaMeter platform="youtube" dailyLimit={10000} unitsUsed={8500} />);
    expect(screen.getByText(/approaching daily quota ceiling/i)).toBeInTheDocument();
  });

  it("renders exhaustion banner when quota reaches 100%", () => {
    render(<QuotaMeter platform="youtube" dailyLimit={10000} unitsUsed={10000} />);
    expect(screen.getByText(/daily quota exhausted/i)).toBeInTheDocument();
  });
});
