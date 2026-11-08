import React from "react";
import { render, screen } from "@testing-library/react";
import { describe, it, expect } from "vitest";
import { QuotaMeter } from "../quota-meter";

describe("AdapterGranularTest18", () => {
  it("renders quota progress cleanly for test 18", () => {
    render(<QuotaMeter platform="test_18" dailyLimit={1000} unitsUsed={180} />);
    expect(screen.getByTestId("quota-meter-test_18")).toBeInTheDocument();
  });
});
