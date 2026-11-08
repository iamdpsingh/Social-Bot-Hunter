import React from "react";
import { render, screen } from "@testing-library/react";
import { describe, it, expect } from "vitest";
import { QuotaMeter } from "../quota-meter";

describe("AdapterGranularTest28", () => {
  it("renders quota progress cleanly for test 28", () => {
    render(<QuotaMeter platform="test_28" dailyLimit={1000} unitsUsed={280} />);
    expect(screen.getByTestId("quota-meter-test_28")).toBeInTheDocument();
  });
});
