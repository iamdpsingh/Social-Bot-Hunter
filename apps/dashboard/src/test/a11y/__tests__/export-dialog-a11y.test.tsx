import React from "react";
import { describe, it, expect, vi } from "vitest";
import { render, screen } from "@testing-library/react";
import { ExportDialog } from "../../../components/investigation/export-dialog";

vi.mock("../../../lib/hooks/use-investigation-export", () => ({
  useInvestigationExport: () => ({
    downloadCsv: vi.fn(),
    downloadJson: vi.fn(),
    isExporting: false,
    error: null,
  }),
}));

describe("ExportDialog Accessibility", () => {
  it("renders accessible dialog structure when open", () => {
    const handleClose = vi.fn();
    render(<ExportDialog isOpen={true} onClose={handleClose} scanId="scan_999" />);

    expect(screen.getByRole("dialog")).toBeInTheDocument();
    expect(screen.getByText("Export Investigation Dataset")).toBeInTheDocument();
  });
});
