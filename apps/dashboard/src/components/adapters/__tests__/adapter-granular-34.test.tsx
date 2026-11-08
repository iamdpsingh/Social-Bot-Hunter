import React from "react";
import { render, screen } from "@testing-library/react";
import { describe, it, expect } from "vitest";
import { QuotaMeter } from "../quota-meter";

describe("AdapterGranularTest34", () => {
  it("renders quota progress cleanly for test 34", () => {
    render(<QuotaMeter platform="test_34" dailyLimit={1000} unitsUsed={340} />);
    expect(screen.getByTestId("quota-meter-test_34")).toBeInTheDocument();
  });
});
