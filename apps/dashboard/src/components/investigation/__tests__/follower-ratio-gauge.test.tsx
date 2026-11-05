import React from "react";
import { describe, it, expect } from "vitest";
import { render, screen } from "@testing-library/react";
import { FollowerRatioGauge } from "../follower-ratio-gauge";

describe("FollowerRatioGauge component", () => {
  it("computes ratio and marks anomalous ratios", () => {
    render(<FollowerRatioGauge followers={10} following={2000} />);
    expect(screen.getByText("Follower-to-Following Ratio")).toBeInTheDocument();
    expect(screen.getByText("Anomalous Ratio")).toBeInTheDocument();
  });
});
