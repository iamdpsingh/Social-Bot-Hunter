import { fireEvent, render, screen } from "@testing-library/react";
import React from "react";
import { describe, expect, it, vi } from "vitest";
import { GraphExportMenu } from "../../../components/graph/graph-export-menu";

describe("Scenario: Analyst exports graph visual and JSON bundle", () => {
  it("opens export dropdown and invokes JSON download", () => {
    const onExportPng = vi.fn();
    const onExportJson = vi.fn();

    render(<GraphExportMenu onExportPng={onExportPng} onExportJson={onExportJson} />);

    fireEvent.click(screen.getByRole("button", { name: "Export ↓" }));
    fireEvent.click(screen.getByRole("menuitem", { name: "Export Graph (JSON)" }));

    expect(onExportJson).toHaveBeenCalledTimes(1);
    expect(onExportPng).not.toHaveBeenCalled();
  });
});
