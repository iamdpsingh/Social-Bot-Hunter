import React from "react";
import { render, screen } from "@testing-library/react";
import { describe, it, expect } from "vitest";
import { QuotaMeter } from "../quota-meter";

describe("AdapterGranularTest17", () => {
  it("renders quota progress cleanly for test 17", () => {
    render(<QuotaMeter platform="test_17" dailyLimit={1000} unitsUsed={170} />);
    expect(screen.getByTestId("quota-meter-test_17")).toBeInTheDocument();
  });
});
