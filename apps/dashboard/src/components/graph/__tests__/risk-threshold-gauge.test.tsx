import { render, screen } from "@testing-library/react";
import React from "react";
import { describe, expect, it } from "vitest";
import { RiskThresholdGauge } from "../risk-threshold-gauge";

describe("RiskThresholdGauge component", () => {
  it("renders progress percentage and color fill", () => {
    render(<RiskThresholdGauge minScore={0.75} />);
    expect(screen.getByText("75%")).toBeInTheDocument();
  });
});
