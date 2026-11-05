import React from "react";
import { describe, it, expect } from "vitest";
import { render, screen } from "@testing-library/react";
import { SignalRadarPreview } from "../../../components/investigation/signal-radar-preview";

describe("Scenario: Signal Radar Heuristic Decomposition", () => {
  it("renders multi-vector percentages with appropriate color classes", () => {
    const { container } = render(
      <SignalRadarPreview
        timingScore={0.92}
        textRepetitionScore={0.78}
        networkAnomalyScore={0.45}
        profileScore={0.12}
      />
    );

    expect(screen.getByText("92%")).toBeInTheDocument();
    expect(screen.getByText("78%")).toBeInTheDocument();
    expect(screen.getByText("45%")).toBeInTheDocument();
    expect(screen.getByText("12%")).toBeInTheDocument();

    const redBars = container.querySelectorAll(".bg-rose-500");
    expect(redBars.length).toBe(2); // > 70%
  });
});
