import React from "react";
import { render, screen } from "@testing-library/react";
import { describe, it, expect } from "vitest";
import { QuotaMeter } from "../quota-meter";

describe("AdapterGranularTest26", () => {
  it("renders quota progress cleanly for test 26", () => {
    render(<QuotaMeter platform="test_26" dailyLimit={1000} unitsUsed={260} />);
    expect(screen.getByTestId("quota-meter-test_26")).toBeInTheDocument();
  });
});
