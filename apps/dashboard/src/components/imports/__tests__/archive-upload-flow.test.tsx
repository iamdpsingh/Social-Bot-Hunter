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
