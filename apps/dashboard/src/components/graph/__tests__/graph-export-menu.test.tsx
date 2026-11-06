import { fireEvent, render, screen } from "@testing-library/react";
import React from "react";
import { describe, expect, it, vi } from "vitest";
import { GraphExportMenu } from "../graph-export-menu";

describe("GraphExportMenu component", () => {
  it("toggles dropdown and dispatches export callbacks", () => {
    const onExportPng = vi.fn();
    const onExportJson = vi.fn();

    render(<GraphExportMenu onExportPng={onExportPng} onExportJson={onExportJson} />);

    const exportBtn = screen.getByRole("button", { name: "Export ↓" });
    fireEvent.click(exportBtn);

    const pngBtn = screen.getByRole("menuitem", { name: "Export Canvas (PNG)" });
    fireEvent.click(pngBtn);
    expect(onExportPng).toHaveBeenCalledTimes(1);

    // Open again for JSON
    fireEvent.click(exportBtn);
    const jsonBtn = screen.getByRole("menuitem", { name: "Export Graph (JSON)" });
    fireEvent.click(jsonBtn);
    expect(onExportJson).toHaveBeenCalledTimes(1);
  });
});
