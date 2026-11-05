import React from "react";
import { describe, it, expect, vi } from "vitest";
import { render, screen, fireEvent } from "@testing-library/react";
import { ExportPanel } from "../export-panel";

describe("ExportPanel", () => {
  it("toggles format and invokes download callbacks", () => {
    const handleCsv = vi.fn();
    const handleJson = vi.fn();

    render(<ExportPanel scanId="s_123" onExportCsv={handleCsv} onExportJson={handleJson} />);
    expect(screen.getByText("Investigation Data Export")).toBeInTheDocument();

    // Default is CSV
    fireEvent.click(screen.getByText("Download CSV"));
    expect(handleCsv).toHaveBeenCalledTimes(1);

    // Switch to JSON
    fireEvent.click(screen.getByText("JSON Bundle"));
    fireEvent.click(screen.getByText("Download JSON"));
    expect(handleJson).toHaveBeenCalledTimes(1);
  });
});
