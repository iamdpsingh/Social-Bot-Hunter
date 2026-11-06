import { render, screen } from "@testing-library/react";
import React from "react";
import { describe, expect, it, vi } from "vitest";
import { NodeDetailDrawer } from "../../../components/graph/node-detail-drawer";

describe("NodeDetailDrawer accessibility", () => {
  const node = { id: "a1", label: "SuspiciousNode", score: 0.85, band: "high" };

  it("provides complementary role and accessible label", () => {
    render(<NodeDetailDrawer scanId="s1" nodeData={node} onClose={vi.fn()} />);
    const drawer = screen.getByRole("complementary", { name: "Account details side panel" });
    expect(drawer).toBeInTheDocument();
    expect(screen.getByRole("button", { name: "Close drawer" })).toBeInTheDocument();
  });
});
