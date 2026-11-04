import React from "react";
import { describe, it, expect } from "vitest";
import { render } from "@testing-library/react";
import Loading from "../loading";

describe("Loading skeleton page", () => {
  it("renders pulse skeleton cards during initial load", () => {
    const { container } = render(<Loading />);
    const skeletons = container.querySelectorAll(".animate-pulse");
    expect(skeletons.length).toBeGreaterThan(0);
  });
});
