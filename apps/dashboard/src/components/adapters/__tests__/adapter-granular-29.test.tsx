import React from "react";
import { render, screen } from "@testing-library/react";
import { describe, it, expect } from "vitest";
import { QuotaMeter } from "../quota-meter";

describe("AdapterGranularTest29", () => {
  it("renders quota progress cleanly for test 29", () => {
    render(<QuotaMeter platform="test_29" dailyLimit={1000} unitsUsed={290} />);
    expect(screen.getByTestId("quota-meter-test_29")).toBeInTheDocument();
  });
});
