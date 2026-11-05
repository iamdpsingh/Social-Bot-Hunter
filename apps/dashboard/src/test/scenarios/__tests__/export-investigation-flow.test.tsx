import React from "react";
import { describe, it, expect, vi } from "vitest";
import { render, screen, fireEvent } from "@testing-library/react";
import { ExportPanel } from "../../../components/investigation/export-panel";

describe("Scenario: Export Investigation Workflow", () => {
  it("dispatches CSV and JSON downloads with confirmation notifications", () => {
    const handleCsv = vi.fn();
    const handleJson = vi.fn();

    render(<ExportPanel scanId="scan_audit_77" onExportCsv={handleCsv} onExportJson={handleJson} />);

    // CSV export
    fireEvent.click(screen.getByText("Download CSV"));
    expect(handleCsv).toHaveBeenCalledTimes(1);
    expect(screen.getByText(/CSV export initiated/)).toBeInTheDocument();

    // Switch to JSON and export
    fireEvent.click(screen.getByText("JSON Bundle"));
    fireEvent.click(screen.getByText("Download JSON"));
    expect(handleJson).toHaveBeenCalledTimes(1);
    expect(screen.getByText(/JSON export bundle initiated/)).toBeInTheDocument();
  });
});
