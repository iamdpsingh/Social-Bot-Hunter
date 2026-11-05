import React from "react";
import { describe, it, expect } from "vitest";
import { render, screen } from "@testing-library/react";
import { MetricPill } from "../metric-pill";

describe("MetricPill component", () => {
  it("renders label and value with mono styling", () => {
    render(<MetricPill label="Evidence Coverage" value="95%" highlight={true} />);
    expect(screen.getByText("Evidence Coverage:")).toBeInTheDocument();
    expect(screen.getByText("95%")).toBeInTheDocument();
  });
});
