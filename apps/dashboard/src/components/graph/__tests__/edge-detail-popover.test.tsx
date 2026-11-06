import { fireEvent, render, screen } from "@testing-library/react";
import React from "react";
import { describe, expect, it, vi } from "vitest";
import { EdgeDetailPopover } from "../edge-detail-popover";

describe("EdgeDetailPopover component", () => {
  it("renders source, target, and relationship type", () => {
    const onClose = vi.fn();
    render(
      <EdgeDetailPopover
        sourceId="node_src"
        targetId="node_tgt"
        relationshipType="retweet"
        onClose={onClose}
      />
    );

    expect(screen.getByText("node_src")).toBeInTheDocument();
    expect(screen.getByText("node_tgt")).toBeInTheDocument();
    expect(screen.getByText("retweet")).toBeInTheDocument();

    fireEvent.click(screen.getByRole("button", { name: "Close edge popover" }));
    expect(onClose).toHaveBeenCalled();
  });
});
