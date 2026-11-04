import { render, screen } from "@testing-library/react";
import { describe, it, expect } from "vitest";
import React from "react";
import { ProgressBar } from "../progress-bar";

describe("ProgressBar component", () => {
  it("renders with percentage width and ARIA attributes", () => {
    render(<ProgressBar value={65} max={100} label="Ingestion Progress" subtext="65/100" />);
    expect(screen.getByText("Ingestion Progress")).toBeInTheDocument();
    expect(screen.getByText("65/100")).toBeInTheDocument();
    const bar = screen.getByRole("progressbar");
    expect(bar).toHaveAttribute("aria-valuenow", "65");
  });

  it("clamps progress to [0, 100]", () => {
    const { rerender } = render(<ProgressBar value={150} max={100} />);
    let bar = screen.getByRole("progressbar");
    expect(bar).toHaveAttribute("aria-valuenow", "100");

    rerender(<ProgressBar value={-20} max={100} />);
    bar = screen.getByRole("progressbar");
    expect(bar).toHaveAttribute("aria-valuenow", "0");
  });
});
