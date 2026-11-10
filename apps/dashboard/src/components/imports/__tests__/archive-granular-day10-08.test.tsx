import React from "react";
import { render, screen } from "@testing-library/react";
import { describe, it, expect, vi } from "vitest";
import { ArchiveUploadModal } from "../archive-upload-modal";

describe("ArchiveGranularDay10_08", () => {
  it("verifies component aspect 08", () => {
    render(<ArchiveUploadModal isOpen={true} onClose={vi.fn()} />);
    expect(screen.getByTestId("archive-upload-modal-content")).toBeInTheDocument();
  });
});
