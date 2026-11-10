import React from "react";
import { render, screen } from "@testing-library/react";
import { describe, it, expect, vi } from "vitest";
import { ArchiveUploadModal } from "../archive-upload-modal";

describe("ArchiveGranularDay10_05", () => {
  it("verifies component aspect 05", () => {
    render(<ArchiveUploadModal isOpen={true} onClose={vi.fn()} />);
    expect(screen.getByTestId("archive-upload-modal-content")).toBeInTheDocument();
  });
});
