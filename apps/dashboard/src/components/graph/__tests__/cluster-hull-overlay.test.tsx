import { render, screen } from "@testing-library/react";
import React from "react";
import { describe, expect, it } from "vitest";
import { ClusterHullOverlay } from "../cluster-hull-overlay";

describe("ClusterHullOverlay component", () => {
  const hulls = [
    {
      clusterId: "c_alpha",
      points: [
        { x: 10, y: 10 },
        { x: 50, y: 10 },
        { x: 30, y: 40 },
      ],
    },
  ];

  it("renders SVG polygon when visible", () => {
    render(<ClusterHullOverlay hulls={hulls} visible={true} />);
    const overlay = screen.getByTestId("cluster-hull-overlay");
    expect(overlay).toBeInTheDocument();
  });

  it("returns null when visible is false", () => {
    const { container } = render(<ClusterHullOverlay hulls={hulls} visible={false} />);
    expect(container.firstChild).toBeNull();
  });
});
