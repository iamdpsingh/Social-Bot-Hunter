import React from "react";
import { render, screen } from "@testing-library/react";
import { describe, it, expect } from "vitest";
import { QuotaMeter } from "../quota-meter";

describe("AdapterGranularTest23", () => {
  it("renders quota progress cleanly for test 23", () => {
    render(<QuotaMeter platform="test_23" dailyLimit={1000} unitsUsed={230} />);
    expect(screen.getByTestId("quota-meter-test_23")).toBeInTheDocument();
  });
});
