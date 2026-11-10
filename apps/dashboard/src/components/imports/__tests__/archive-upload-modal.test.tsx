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

  it("accepts valid zip file on input change", () => {
    render(<ArchiveUploadModal isOpen={true} onClose={vi.fn()} />);
    const input = screen.getByTestId("archive-file-input") as HTMLInputElement;
    const file = new File(["test-content"], "dataset.zip", { type: "application/zip" });
    Object.defineProperty(input, "files", { value: [file] });
    input.dispatchEvent(new Event("change", { bubbles: true }));
    expect(screen.getByText("dataset.zip")).toBeInTheDocument();
  });

  it("shows error on oversized archive file", () => {
    render(<ArchiveUploadModal isOpen={true} onClose={vi.fn()} />);
    const input = screen.getByTestId("archive-file-input") as HTMLInputElement;
    const bigFile = new File([""], "huge.zip", { type: "application/zip" });
    Object.defineProperty(bigFile, "size", { value: 200 * 1024 * 1024 });
    Object.defineProperty(input, "files", { value: [bigFile] });
    input.dispatchEvent(new Event("change", { bubbles: true }));
    expect(screen.getByTestId("error-banner")).toBeInTheDocument();
    expect(screen.getByText(/Archive exceeds client size limit/i)).toBeInTheDocument();
  });
});
