import { render, screen } from "@testing-library/react";
import React from "react";
import { describe, expect, it, vi } from "vitest";
import { NeighborExpandModal } from "../../../components/graph/neighbor-expand-modal";

describe("NeighborExpandModal accessibility", () => {
  it("provides dialog role with aria-modal and labelledby", () => {
    render(
      <NeighborExpandModal
        nodeId="acc_target"
        isOpen={true}
        onClose={vi.fn()}
        onExpand={vi.fn()}
      />
    );
    const dialog = screen.getByRole("dialog");
    expect(dialog).toHaveAttribute("aria-modal", "true");
    expect(dialog).toHaveAttribute("aria-labelledby", "expand-modal-title");
  });
});
