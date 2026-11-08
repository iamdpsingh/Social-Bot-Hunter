import React from "react";
import { render, screen } from "@testing-library/react";
import { describe, it, expect } from "vitest";
import { QuotaMeter } from "../../../components/adapters/quota-meter";

describe("A11y: QuotaMeter", () => {
  it("provides standard progressbar role with aria values", () => {
    render(<QuotaMeter platform="youtube" dailyLimit={10000} unitsUsed={5000} />);
    const progressbar = screen.getByRole("progressbar");
    expect(progressbar).toHaveAttribute("aria-valuenow", "50");
    expect(progressbar).toHaveAttribute("aria-valuemin", "0");
    expect(progressbar).toHaveAttribute("aria-valuemax", "100");
    expect(progressbar).toHaveAttribute("aria-label", "youtube API Quota Usage");
  });
});
