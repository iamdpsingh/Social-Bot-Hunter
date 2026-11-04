import { render, screen } from "@testing-library/react";
import { describe, it, expect } from "vitest";
import React from "react";
import { PlatformIcon } from "../platform-icon";

describe("PlatformIcon component", () => {
  it("renders X (Twitter) icon", () => {
    render(<PlatformIcon platform="x" />);
    expect(screen.getByLabelText("X (Twitter)")).toBeInTheDocument();
  });

  it("renders Instagram icon", () => {
    render(<PlatformIcon platform="instagram" />);
    expect(screen.getByLabelText("Instagram")).toBeInTheDocument();
  });

  it("renders YouTube icon", () => {
    render(<PlatformIcon platform="youtube" />);
    expect(screen.getByLabelText("YouTube")).toBeInTheDocument();
  });

  it("renders TikTok icon", () => {
    render(<PlatformIcon platform="tiktok" />);
    expect(screen.getByLabelText("TikTok")).toBeInTheDocument();
  });

  it("renders LinkedIn icon", () => {
    render(<PlatformIcon platform="linkedin" />);
    expect(screen.getByLabelText("LinkedIn")).toBeInTheDocument();
  });
});
