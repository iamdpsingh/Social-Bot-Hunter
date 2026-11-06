import { fireEvent, render, screen } from "@testing-library/react";
import React from "react";
import { describe, expect, it, vi } from "vitest";
import { NeighborExpandModal } from "../neighbor-expand-modal";

describe("NeighborExpandModal component", () => {
  it("renders modal options and applies selected expansion parameters", () => {
    const onExpand = vi.fn();
    const onClose = vi.fn();

    render(
      <NeighborExpandModal
        nodeId="bot_central"
        isOpen={true}
        onClose={onClose}
        onExpand={onExpand}
      />
    );

    expect(screen.getByText("Expand Ego Network")).toBeInTheDocument();
    fireEvent.click(screen.getByRole("button", { name: "in" }));
    fireEvent.click(screen.getByRole("button", { name: "2 Hops" }));
    fireEvent.click(screen.getByRole("button", { name: "Apply Expansion" }));

    expect(onExpand).toHaveBeenCalledWith("in", 2);
    expect(onClose).toHaveBeenCalled();
  });

  it("returns null when isOpen is false", () => {
    const { container } = render(
      <NeighborExpandModal
        nodeId="bot_central"
        isOpen={false}
        onClose={vi.fn()}
        onExpand={vi.fn()}
      />
    );
    expect(container.firstChild).toBeNull();
  });
});
