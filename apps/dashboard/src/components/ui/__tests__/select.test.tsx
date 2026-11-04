import React from "react";
import { describe, it, expect, vi } from "vitest";
import { render, screen, fireEvent } from "@testing-library/react";
import { Select } from "../select";

describe("Select component", () => {
  const options = [
    { value: "x", label: "X / Twitter" },
    { value: "instagram", label: "Instagram" },
    { value: "tiktok", label: "TikTok" },
  ];

  it("renders select with label and options", () => {
    render(<Select label="Platform" options={options} />);
    expect(screen.getByLabelText("Platform")).toBeInTheDocument();
    expect(screen.getByText("X / Twitter")).toBeInTheDocument();
    expect(screen.getByText("Instagram")).toBeInTheDocument();
    expect(screen.getByText("TikTok")).toBeInTheDocument();
  });

  it("triggers onChange when selection changes", () => {
    const handleChange = vi.fn();
    render(<Select label="Platform" options={options} onChange={handleChange} />);
    const select = screen.getByLabelText("Platform");
    fireEvent.change(select, { target: { value: "instagram" } });
    expect(handleChange).toHaveBeenCalled();
  });
});
