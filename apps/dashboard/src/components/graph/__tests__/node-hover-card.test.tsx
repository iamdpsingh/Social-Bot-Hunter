import { render, screen } from "@testing-library/react";
import React from "react";
import { describe, expect, it } from "vitest";
import { NodeHoverCard } from "../node-hover-card";

describe("NodeHoverCard component", () => {
  it("renders node label and score", () => {
    const node = { id: "n1", label: "AlphaBot", score: 0.88 };
    render(<NodeHoverCard nodeData={node} />);
    expect(screen.getByText("AlphaBot")).toBeInTheDocument();
    expect(screen.getByText("Score: 88%")).toBeInTheDocument();
  });

  it("returns null when nodeData is null", () => {
    const { container } = render(<NodeHoverCard nodeData={null} />);
    expect(container.firstChild).toBeNull();
  });
});
