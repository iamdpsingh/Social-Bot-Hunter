import React from "react";
import { describe, it, expect } from "vitest";
import { render, screen } from "@testing-library/react";
import { ExportDialog } from "../export-dialog";

describe("ExportDialog component", () => {
  it("renders format selection buttons and download trigger", () => {
    render(<ExportDialog isOpen={true} onClose={() => {}} scanId="scan_10" isSynthetic={true} />);
    expect(screen.getByText("Export Investigation Results")).toBeInTheDocument();
    expect(screen.getByText("RFC 4180 CSV")).toBeInTheDocument();
    expect(screen.getByText("JSON Evidence Bundle")).toBeInTheDocument();
    expect(screen.getByText(/Download CSV/)).toBeInTheDocument();
  });
});
