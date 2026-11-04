import React from "react";
import { describe, it, expect, vi } from "vitest";
import { render, screen, fireEvent } from "@testing-library/react";
import { Input } from "../input";

describe("Input component", () => {
  it("renders input with label and helper text", () => {
    render(<Input label="Target Handle" helperText="Enter social username" placeholder="@target" />);
    expect(screen.getByLabelText("Target Handle")).toBeInTheDocument();
    expect(screen.getByText("Enter social username")).toBeInTheDocument();
    expect(screen.getByPlaceholderText("@target")).toBeInTheDocument();
  });

  it("displays validation error message", () => {
    render(<Input label="Target Handle" error="Username cannot be empty" />);
    expect(screen.getByText("Username cannot be empty")).toBeInTheDocument();
  });

  it("handles user typing events", () => {
    const handleChange = vi.fn();
    render(<Input label="Handle" onChange={handleChange} />);
    const input = screen.getByLabelText("Handle");
    fireEvent.change(input, { target: { value: "testuser" } });
    expect(handleChange).toHaveBeenCalled();
  });
});
