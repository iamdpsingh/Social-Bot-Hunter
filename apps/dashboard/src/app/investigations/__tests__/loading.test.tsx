import React from "react";
import { describe, it, expect } from "vitest";
import { render } from "@testing-library/react";
import InvestigationsLoading from "../loading";

describe("InvestigationsLoading", () => {
  it("renders placeholder pulse elements", () => {
    const { container } = render(<InvestigationsLoading />);
    const skeletons = container.querySelectorAll(".animate-pulse");
    expect(skeletons.length).toBeGreaterThan(0);
  });
});
