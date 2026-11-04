import React from "react";
import { describe, it, expect } from "vitest";
import { render, screen } from "@testing-library/react";
import { MetricTrend } from "../metric-trend";

describe("MetricTrend component", () => {
  it("renders positive trend with upward arrow", () => {
    render(<MetricTrend value={14} direction="up" label="vs last week" />);
    expect(screen.getByTestId("trend-up")).toBeInTheDocument();
    expect(screen.getByText("14%")).toBeInTheDocument();
    expect(screen.getByText("vs last week")).toBeInTheDocument();
  });

  it("renders negative trend with downward arrow", () => {
    render(<MetricTrend value={8} direction="down" />);
    expect(screen.getByTestId("trend-down")).toBeInTheDocument();
    expect(screen.getByText("8%")).toBeInTheDocument();
  });
});
