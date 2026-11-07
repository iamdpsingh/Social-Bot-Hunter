import { render, screen } from "@testing-library/react";
import { describe, it, expect } from "vitest";
import { CoverageGapBanner } from "../../../../components/diff/coverage-gap-banner";

describe("Scenario: Coverage Gap Transparency", () => {
  it("prominently informs analyst of coverage gaps vs real removals", () => {
    render(<CoverageGapBanner coverageGapsCount={7} />);
    const banner = screen.getByTestId("coverage-gap-banner");
    expect(banner).toBeInTheDocument();
    expect(banner).toHaveTextContent("Coverage Gap Transparency (7 unobserved accounts)");
    expect(banner).toHaveTextContent("Social Bot Hunter strictly distinguishes between proven removals");
  });
});
