import React from "react";
import { render, screen } from "@testing-library/react";
import { describe, it, expect } from "vitest";
import { QuotaMeter } from "../quota-meter";

describe("AdapterGranularTest22", () => {
  it("renders quota progress cleanly for test 22", () => {
    render(<QuotaMeter platform="test_22" dailyLimit={1000} unitsUsed={220} />);
    expect(screen.getByTestId("quota-meter-test_22")).toBeInTheDocument();
  });
});
