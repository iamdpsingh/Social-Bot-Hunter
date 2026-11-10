import React from "react";
import { render, screen } from "@testing-library/react";
import { describe, it, expect, vi } from "vitest";
import { ArchiveUploadModal } from "../archive-upload-modal";

describe("ArchiveUploadModal", () => {
  it("does not render when isOpen is false", () => {
    render(<ArchiveUploadModal isOpen={false} onClose={vi.fn()} />);
    expect(screen.queryByTestId("archive-upload-modal-content")).not.toBeInTheDocument();
  });
