import { fireEvent, render, screen } from "@testing-library/react";
import React from "react";
import { describe, expect, it, vi } from "vitest";
import { EgoExpansionBanner } from "../ego-expansion-banner";

describe("EgoExpansionBanner component", () => {
  it("renders center node and triggers reset callback", () => {
    const onReset = vi.fn();
    render(<EgoExpansionBanner centerNodeId="acc_focal" radius={2} onResetExpansion={onReset} />);

    expect(screen.getByText("acc_focal")).toBeInTheDocument();
    expect(screen.getByText(/2 hops/)).toBeInTheDocument();

    fireEvent.click(screen.getByRole("button", { name: "Reset Expansion" }));
    expect(onReset).toHaveBeenCalledTimes(1);
  });
});
