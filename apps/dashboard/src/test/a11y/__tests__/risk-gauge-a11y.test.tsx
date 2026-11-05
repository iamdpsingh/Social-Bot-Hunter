import React from "react";
import { describe, it, expect } from "vitest";
import { render, screen } from "@testing-library/react";
import { RiskGauge } from "../../../components/investigation/risk-gauge";

describe("RiskGauge Accessibility", () => {
  it("renders meter role with aria-valuenow and aria-valuetext", () => {
    render(<RiskGauge score={0.78} size="md" />);
    const meter = screen.getByRole("meter");
    expect(meter).toBeInTheDocument();
    expect(meter).toHaveAttribute("aria-valuenow", "78");
    expect(meter).toHaveAttribute("aria-valuemin", "0");
    expect(meter).toHaveAttribute("aria-valuemax", "100");
  });
});
