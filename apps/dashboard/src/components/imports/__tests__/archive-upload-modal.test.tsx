import React from "react";
import { render, screen } from "@testing-library/react";
import { describe, it, expect, vi } from "vitest";
import { ArchiveUploadModal } from "../archive-upload-modal";

describe("ArchiveUploadModal", () => {
  it("does not render when isOpen is false", () => {
    render(<ArchiveUploadModal isOpen={false} onClose={vi.fn()} />);
    expect(screen.queryByTestId("archive-upload-modal-content")).not.toBeInTheDocument();
  });

  it("renders dropzone and file input when open", () => {
    render(<ArchiveUploadModal isOpen={true} onClose={vi.fn()} />);
    expect(screen.getByTestId("archive-dropzone")).toBeInTheDocument();
    expect(screen.getByTestId("archive-file-input")).toBeInTheDocument();
  });
