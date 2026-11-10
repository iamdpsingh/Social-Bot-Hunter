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

  it("shows ndjson format badge when ndjson stream extracted", async () => {
    global.fetch = vi.fn().mockResolvedValue({
      ok: true,
      json: async () => ({
        status: "extracted",
        archive_format: "ndjson",
        file_count: 1,
        uncompressed_bytes: 8000,
        platform_detected: null,
        extracted_path: "/tmp/ndjson",
      }),
    });
    render(<ArchiveUploadModal isOpen={true} onClose={vi.fn()} />);
    fireEvent.change(screen.getByTestId("archive-file-input"), {
      target: { files: [new File([""], "feed.ndjson")] },
    });
    fireEvent.click(screen.getByTestId("start-upload-button"));
    await waitFor(() => screen.getByTestId("extracted-summary"));
    expect(screen.getByText("ndjson")).toBeInTheDocument();
  });

  it("shows csv format badge when csv table extracted", async () => {
    global.fetch = vi.fn().mockResolvedValue({
      ok: true,
      json: async () => ({
        status: "extracted",
        archive_format: "csv",
        file_count: 2,
        uncompressed_bytes: 4000,
        platform_detected: null,
        extracted_path: "/tmp/csv",
      }),
    });
    render(<ArchiveUploadModal isOpen={true} onClose={vi.fn()} />);
    fireEvent.change(screen.getByTestId("archive-file-input"), {
      target: { files: [new File([""], "table.csv")] },
    });
    fireEvent.click(screen.getByTestId("start-upload-button"));
    await waitFor(() => screen.getByTestId("extracted-summary"));
    expect(screen.getByText("csv")).toBeInTheDocument();
  });

  it("displays error banner when security violation returned", async () => {
    global.fetch = vi.fn().mockResolvedValue({
      ok: false,
      status: 400,
      json: async () => ({
        detail: { message: "Compression ratio exceeds safety threshold (zip-bomb detected)" },
      }),
    });
    render(<ArchiveUploadModal isOpen={true} onClose={vi.fn()} />);
    fireEvent.change(screen.getByTestId("archive-file-input"), {
      target: { files: [new File([""], "bomb.zip")] },
    });
    fireEvent.click(screen.getByTestId("start-upload-button"));
    await waitFor(() => screen.getByTestId("error-banner"));
    expect(screen.getByText(/zip-bomb detected/i)).toBeInTheDocument();
  });
});
