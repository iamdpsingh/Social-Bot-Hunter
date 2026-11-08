import React from "react";
import { render, screen } from "@testing-library/react";
import { describe, it, expect } from "vitest";
import { QuotaMeter } from "../quota-meter";

describe("AdapterGranularTest33", () => {
  it("renders quota progress cleanly for test 33", () => {
    render(<QuotaMeter platform="test_33" dailyLimit={1000} unitsUsed={330} />);
    expect(screen.getByTestId("quota-meter-test_33")).toBeInTheDocument();
  });
});
