import React from "react";
import { describe, it, expect } from "vitest";
import { render } from "@testing-library/react";
import AccountDetailLoading from "../loading";

describe("AccountDetailLoading", () => {
  it("renders account detail skeleton placeholders", () => {
    const { container } = render(<AccountDetailLoading />);
    const skeletons = container.querySelectorAll(".animate-pulse");
    expect(skeletons.length).toBeGreaterThan(0);
  });
});
