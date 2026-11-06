import { fireEvent, render, screen } from "@testing-library/react";
import React from "react";
import { describe, expect, it, vi } from "vitest";
import { NeighborExpandModal } from "../../../components/graph/neighbor-expand-modal";

describe("Scenario: Analyst executes ego-expansion around suspicious node", () => {
  it("opens expansion modal and selects 2-hop radius outbound traversal", () => {
    const onExpand = vi.fn();
    render(
      <NeighborExpandModal
        nodeId="botnet_controller"
        isOpen={true}
        onClose={vi.fn()}
        onExpand={onExpand}
      />
    );

    fireEvent.click(screen.getByRole("button", { name: "out" }));
    fireEvent.click(screen.getByRole("button", { name: "2 Hops" }));
    fireEvent.click(screen.getByRole("button", { name: "Apply Expansion" }));

    expect(onExpand).toHaveBeenCalledWith("out", 2);
  });
});
