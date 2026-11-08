import React from "react";
import { render, screen } from "@testing-library/react";
import { describe, it, expect } from "vitest";
import { QuotaMeter } from "../quota-meter";

describe("AdapterGranularTest20", () => {
  it("renders quota progress cleanly for test 20", () => {
    render(<QuotaMeter platform="test_20" dailyLimit={1000} unitsUsed={200} />);
    expect(screen.getByTestId("quota-meter-test_20")).toBeInTheDocument();
  });
});
