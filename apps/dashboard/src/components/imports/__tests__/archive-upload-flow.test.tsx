import React from "react";
import { render, screen, fireEvent, waitFor } from "@testing-library/react";
import { describe, it, expect, vi, beforeEach } from "vitest";
import { ArchiveUploadModal } from "../archive-upload-modal";

describe("ArchiveUploadModal Flow", () => {
  beforeEach(() => {
    vi.restoreAllMocks();
  });

  it("renders upload button disabled until file selected", () => {
    render(<ArchiveUploadModal isOpen={true} onClose={vi.fn()} />);
    const btn = screen.getByTestId("start-upload-button");
    expect(btn).toBeDisabled();
  });

  it("displays extracted summary on successful upload", async () => {
    global.fetch = vi.fn().mockResolvedValue({
      ok: true,
      json: async () => ({
        status: "extracted",
        archive_format: "twitter_archive",
        file_count: 5,
        uncompressed_bytes: 45000,
        platform_detected: "x",
        extracted_path: "/tmp/sbh/extracted",
      }),
    });
    const handleSuccess = vi.fn();
    render(<ArchiveUploadModal isOpen={true} onClose={vi.fn()} onSuccess={handleSuccess} />);
    const input = screen.getByTestId("archive-file-input");
    const file = new File(["dummy"], "twitter.zip", { type: "application/zip" });
    fireEvent.change(input, { target: { files: [file] } });
    const uploadBtn = screen.getByTestId("start-upload-button");
    expect(uploadBtn).not.toBeDisabled();
    fireEvent.click(uploadBtn);
    await waitFor(() => {
      expect(screen.getByTestId("extracted-summary")).toBeInTheDocument();
    });
    expect(screen.getByText("twitter_archive")).toBeInTheDocument();
    expect(handleSuccess).toHaveBeenCalledWith("/tmp/sbh/extracted", "twitter_archive", 5);
  });

  it("shows twitter_archive badge with correct styling", async () => {
    global.fetch = vi.fn().mockResolvedValue({
      ok: true,
      json: async () => ({
        status: "extracted",
        archive_format: "twitter_archive",
        file_count: 10,
        uncompressed_bytes: 12000,
        platform_detected: "x",
        extracted_path: "/tmp/twitter",
      }),
    });
    render(<ArchiveUploadModal isOpen={true} onClose={vi.fn()} />);
    fireEvent.change(screen.getByTestId("archive-file-input"), {
      target: { files: [new File([""], "archive.zip")] },
    });
    fireEvent.click(screen.getByTestId("start-upload-button"));
    await waitFor(() => screen.getByTestId("extracted-summary"));
    expect(screen.getByText("twitter_archive")).toBeInTheDocument();
  });
