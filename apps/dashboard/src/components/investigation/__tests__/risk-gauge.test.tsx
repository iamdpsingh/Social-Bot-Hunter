import React from "react";
import { describe, it, expect } from "vitest";
import { render, screen } from "@testing-library/react";
import { RiskGauge } from "../risk-gauge";

describe("RiskGauge component", () => {
  it("renders percentage score and risk label", () => {
    render(<RiskGauge score={0.78} band="high" />);
    expect(screen.getByText("78%")).toBeInTheDocument();
    expect(screen.getByText("Bot Risk")).toBeInTheDocument();
    expect(screen.getByText("High Risk")).toBeInTheDocument();
  });

  it("handles null score gracefully", () => {
    render(<RiskGauge score={null} />);
    expect(screen.getByText("N/A")).toBeInTheDocument();
  });
});
