import React from "react";
import { render, screen } from "@testing-library/react";
import { describe, it, expect } from "vitest";
import { QuotaMeter } from "../quota-meter";

describe("AdapterGranularTest21", () => {
  it("renders quota progress cleanly for test 21", () => {
    render(<QuotaMeter platform="test_21" dailyLimit={1000} unitsUsed={210} />);
    expect(screen.getByTestId("quota-meter-test_21")).toBeInTheDocument();
  });
});
