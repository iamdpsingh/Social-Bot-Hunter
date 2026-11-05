import React from "react";
import { describe, it, expect } from "vitest";
import { render, screen } from "@testing-library/react";
import { SignalRadarPreview } from "../signal-radar-preview";

describe("SignalRadarPreview", () => {
  it("renders behavioral vector progress bars with percentage values", () => {
    render(
      <SignalRadarPreview
        timingScore={0.85}
        textRepetitionScore={0.65}
        networkAnomalyScore={0.3}
        profileScore={0.15}
      />
    );

    expect(screen.getByText("Activity Timing")).toBeInTheDocument();
    expect(screen.getByText("85%")).toBeInTheDocument();
    expect(screen.getByText("Text Repetition")).toBeInTheDocument();
    expect(screen.getByText("65%")).toBeInTheDocument();
  });
});
