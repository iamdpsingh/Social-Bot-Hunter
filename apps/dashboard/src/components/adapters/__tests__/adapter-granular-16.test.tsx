import React from "react";
import { render, screen } from "@testing-library/react";
import { describe, it, expect } from "vitest";
import { QuotaMeter } from "../quota-meter";

describe("AdapterGranularTest16", () => {
  it("renders quota progress cleanly for test 16", () => {
    render(<QuotaMeter platform="test_16" dailyLimit={1000} unitsUsed={160} />);
    expect(screen.getByTestId("quota-meter-test_16")).toBeInTheDocument();
  });
});
