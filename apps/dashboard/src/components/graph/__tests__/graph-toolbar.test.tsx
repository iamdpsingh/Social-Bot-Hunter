import { fireEvent, render, screen } from "@testing-library/react";
import React from "react";
import { describe, expect, it, vi } from "vitest";
import { GraphToolbar } from "../graph-toolbar";

describe("GraphToolbar component", () => {
  it("renders zoom, fit, reset buttons and dispatches callbacks", () => {
    const onZoomIn = vi.fn();
    const onZoomOut = vi.fn();
    const onFit = vi.fn();
    const onReset = vi.fn();
    const onChangeLayout = vi.fn();

    render(
      <GraphToolbar
        layoutPreset="cose"
        onChangeLayout={onChangeLayout}
        onZoomIn={onZoomIn}
        onZoomOut={onZoomOut}
        onFit={onFit}
        onReset={onReset}
      />
    );

    fireEvent.click(screen.getByRole("button", { name: "Zoom in" }));
    expect(onZoomIn).toHaveBeenCalledTimes(1);

    fireEvent.click(screen.getByRole("button", { name: "Zoom out" }));
    expect(onZoomOut).toHaveBeenCalledTimes(1);

    fireEvent.click(screen.getByRole("button", { name: "Fit to screen" }));
    expect(onFit).toHaveBeenCalledTimes(1);

    fireEvent.click(screen.getByRole("button", { name: "Reset view" }));
    expect(onReset).toHaveBeenCalledTimes(1);
  });

  it("handles layout change selection", () => {
    const onChangeLayout = vi.fn();
    render(
      <GraphToolbar
        layoutPreset="cose"
        onChangeLayout={onChangeLayout}
        onZoomIn={vi.fn()}
        onZoomOut={vi.fn()}
        onFit={vi.fn()}
        onReset={vi.fn()}
      />
    );

    const select = screen.getByLabelText("Layout:");
    fireEvent.change(select, { target: { value: "concentric" } });
    expect(onChangeLayout).toHaveBeenCalledWith("concentric");
  });
});
