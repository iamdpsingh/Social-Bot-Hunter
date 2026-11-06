import { render, screen } from "@testing-library/react";
import React from "react";
import { describe, expect, it } from "vitest";
import { GraphLoadingSkeleton } from "../graph-loading-skeleton";

describe("GraphLoadingSkeleton component", () => {
  it("renders loading message and spinner", () => {
    render(<GraphLoadingSkeleton />);
    expect(screen.getByTestId("graph-loading-skeleton")).toBeInTheDocument();
    expect(screen.getByText(/Constructing graph elements/)).toBeInTheDocument();
  });
});
