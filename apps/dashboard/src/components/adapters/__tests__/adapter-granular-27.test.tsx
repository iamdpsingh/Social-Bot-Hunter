import React from "react";
import { render, screen } from "@testing-library/react";
import { describe, it, expect } from "vitest";
import { QuotaMeter } from "../quota-meter";

describe("AdapterGranularTest27", () => {
  it("renders quota progress cleanly for test 27", () => {
    render(<QuotaMeter platform="test_27" dailyLimit={1000} unitsUsed={270} />);
    expect(screen.getByTestId("quota-meter-test_27")).toBeInTheDocument();
  });
});
