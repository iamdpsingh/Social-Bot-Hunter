import { fireEvent, render, screen } from "@testing-library/react";
import React from "react";
import { describe, expect, it, vi } from "vitest";
import { GraphEmptyState } from "../graph-empty-state";

describe("GraphEmptyState component", () => {
  it("renders empty state message and triggers filter reset", () => {
    const onReset = vi.fn();
    render(<GraphEmptyState onResetFilters={onReset} />);

    expect(screen.getByText("No Graph Nodes Match Active Filters")).toBeInTheDocument();
    fireEvent.click(screen.getByRole("button", { name: "Reset All Filters" }));
    expect(onReset).toHaveBeenCalledTimes(1);
  });
});
