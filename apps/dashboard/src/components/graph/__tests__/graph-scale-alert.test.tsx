import { fireEvent, render, screen } from "@testing-library/react";
import React from "react";
import { describe, expect, it, vi } from "vitest";
import { GraphScaleAlert } from "../graph-scale-alert";

describe("GraphScaleAlert component", () => {
  it("renders warning when nodeCount exceeds 5000", () => {
    const onSwitch = vi.fn();
    render(<GraphScaleAlert nodeCount={8500} onSwitchToTable={onSwitch} />);

    expect(screen.getByText(/Large network detected/)).toBeInTheDocument();
    expect(screen.getByText("8,500")).toBeInTheDocument();

    fireEvent.click(screen.getByRole("button", { name: "Switch to Table View" }));
    expect(onSwitch).toHaveBeenCalledTimes(1);
  });

  it("returns null when nodeCount is under threshold", () => {
    const { container } = render(<GraphScaleAlert nodeCount={4900} onSwitchToTable={vi.fn()} />);
    expect(container.firstChild).toBeNull();
  });
});
