import { fireEvent, render, screen } from "@testing-library/react";
import React from "react";
import { describe, expect, it, vi } from "vitest";
import { ViewModeToggle } from "../view-mode-toggle";

describe("ViewModeToggle component", () => {
  it("toggles between canvas and table view modes", () => {
    const onChange = vi.fn();
    render(<ViewModeToggle viewMode="canvas" onViewModeChange={onChange} />);

    expect(screen.getByRole("button", { name: "Interactive Canvas" })).toHaveAttribute("aria-pressed", "true");
    expect(screen.getByRole("button", { name: "Accessible Table" })).toHaveAttribute("aria-pressed", "false");

    fireEvent.click(screen.getByRole("button", { name: "Accessible Table" }));
    expect(onChange).toHaveBeenCalledWith("table");
  });
});
