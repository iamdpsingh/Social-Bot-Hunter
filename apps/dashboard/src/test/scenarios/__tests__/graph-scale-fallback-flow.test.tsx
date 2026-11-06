import { fireEvent, render, screen } from "@testing-library/react";
import React from "react";
import { describe, expect, it, vi } from "vitest";
import { GraphScaleAlert } from "../../../components/graph/graph-scale-alert";

describe("Scenario: Large graph scale triggers fallback recommendation", () => {
  it("detects 6,500 nodes and switches to accessible table view", () => {
    const onSwitch = vi.fn();
    render(<GraphScaleAlert nodeCount={6500} onSwitchToTable={onSwitch} />);

    expect(screen.getByText(/6,500/)).toBeInTheDocument();
    fireEvent.click(screen.getByRole("button", { name: "Switch to Table View" }));
    expect(onSwitch).toHaveBeenCalledTimes(1);
  });
});
