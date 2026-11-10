import React from "react";
import { render, screen } from "@testing-library/react";
import { describe, it, expect, vi } from "vitest";
import { ArchiveUploadModal } from "../archive-upload-modal";

describe("ArchiveUploadModal A11y", () => {
  it("has accessible dialog role and title", () => {
    render(<ArchiveUploadModal isOpen={true} onClose={vi.fn()} />);
    const dialog = screen.getByRole("dialog");
    expect(dialog).toBeInTheDocument();
    expect(screen.getByText(/dataset archive ingestion & security inspection/i)).toBeInTheDocument();
  });
