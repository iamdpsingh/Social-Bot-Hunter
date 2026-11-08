import React from "react";
import { render, screen } from "@testing-library/react";
import { describe, it, expect } from "vitest";
import { QuotaMeter } from "../quota-meter";

describe("AdapterGranularTest31", () => {
  it("renders quota progress cleanly for test 31", () => {
    render(<QuotaMeter platform="test_31" dailyLimit={1000} unitsUsed={310} />);
    expect(screen.getByTestId("quota-meter-test_31")).toBeInTheDocument();
  });
});
