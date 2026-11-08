import React from "react";
import { render, screen } from "@testing-library/react";
import { describe, it, expect } from "vitest";
import { QuotaMeter } from "../quota-meter";

describe("AdapterGranularTest32", () => {
  it("renders quota progress cleanly for test 32", () => {
    render(<QuotaMeter platform="test_32" dailyLimit={1000} unitsUsed={320} />);
    expect(screen.getByTestId("quota-meter-test_32")).toBeInTheDocument();
  });
});
