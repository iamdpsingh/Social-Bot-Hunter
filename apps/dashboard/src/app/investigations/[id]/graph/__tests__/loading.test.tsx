import { render, screen } from "@testing-library/react";
import React from "react";
import { describe, expect, it } from "vitest";
import Loading from "../loading";

describe("InvestigationGraph Loading component", () => {
  it("renders loading skeleton placeholder", () => {
    render(<Loading />);
    expect(screen.getByTestId("graph-loading-skeleton")).toBeInTheDocument();
  });
});
