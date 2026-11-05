import React from "react";
import { describe, it, expect } from "vitest";
import { render, screen } from "@testing-library/react";
import { ContributingSignalBar } from "../contributing-signal-bar";

describe("ContributingSignalBar component", () => {
  it("renders intensity percentage and progress track", () => {
    render(<ContributingSignalBar value={0.82} weight={0.3} />);
    expect(screen.getByText("Signal Intensity")).toBeInTheDocument();
    expect(screen.getByText("82%")).toBeInTheDocument();
  });
});
