import React from "react";
import { describe, it, expect } from "vitest";
import { render, screen, fireEvent } from "@testing-library/react";
import { Tooltip } from "../tooltip";

describe("Tooltip component", () => {
  it("shows tooltip content on hover and hides on mouse leave", () => {
    render(
      <Tooltip content="API Latency: 12ms">
        <button>Health Info</button>
      </Tooltip>
    );

    expect(screen.queryByRole("tooltip")).not.toBeInTheDocument();
    fireEvent.mouseEnter(screen.getByText("Health Info").parentElement!);
    expect(screen.getByRole("tooltip")).toBeInTheDocument();
    expect(screen.getByText("API Latency: 12ms")).toBeInTheDocument();

    fireEvent.mouseLeave(screen.getByText("Health Info").parentElement!);
    expect(screen.queryByRole("tooltip")).not.toBeInTheDocument();
  });
});
