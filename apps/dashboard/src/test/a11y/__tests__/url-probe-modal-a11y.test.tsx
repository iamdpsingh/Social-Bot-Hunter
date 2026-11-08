import React from "react";
import { render, screen } from "@testing-library/react";
import { describe, it, expect, vi } from "vitest";
import { UrlProbeModal } from "../../../components/adapters/url-probe-modal";

describe("A11y: UrlProbeModal", () => {
  it("provides accessible form controls and dialog landmarks", () => {
    render(<UrlProbeModal isOpen={true} onClose={vi.fn()} />);
    const dialog = screen.getByRole("dialog");
    expect(dialog).toBeInTheDocument();
    expect(screen.getByLabelText(/Target Account Profile URL or Handle/i)).toBeInTheDocument();
  });
});
