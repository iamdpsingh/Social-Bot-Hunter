import { render, screen } from "@testing-library/react";
import React from "react";
import { describe, expect, it } from "vitest";
import { GraphLegend } from "../graph-legend";

describe("GraphLegend component", () => {
  it("renders all risk band labels and arrow semantics", () => {
    render(<GraphLegend />);
    expect(screen.getByText("Critical")).toBeInTheDocument();
    expect(screen.getByText("High")).toBeInTheDocument();
    expect(screen.getByText("Medium")).toBeInTheDocument();
    expect(screen.getByText("Low")).toBeInTheDocument();
    expect(screen.getByText("Insufficient")).toBeInTheDocument();
    expect(screen.getByText(/Follower → Following/)).toBeInTheDocument();
  });
});
