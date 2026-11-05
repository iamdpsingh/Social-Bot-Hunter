import React from "react";
import { describe, it, expect } from "vitest";
import { render } from "@testing-library/react";
import InvestigationDetailLoading from "../loading";

describe("InvestigationDetailLoading", () => {
  it("renders loading skeleton elements", () => {
    const { container } = render(<InvestigationDetailLoading />);
    const skeletons = container.querySelectorAll(".animate-pulse");
    expect(skeletons.length).toBeGreaterThan(0);
  });
});
