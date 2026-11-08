import React from "react";
import { render, screen } from "@testing-library/react";
import { describe, it, expect } from "vitest";
import { QuotaMeter } from "../quota-meter";

describe("AdapterGranularTest30", () => {
  it("renders quota progress cleanly for test 30", () => {
    render(<QuotaMeter platform="test_30" dailyLimit={1000} unitsUsed={300} />);
    expect(screen.getByTestId("quota-meter-test_30")).toBeInTheDocument();
  });
});
