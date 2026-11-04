"use client";

import React, { useState } from "react";
import { cn } from "../../lib/utils";

export interface TooltipProps {
  content: React.ReactNode;
  children: React.ReactElement;
  position?: "top" | "bottom" | "left" | "right";
  className?: string;
}

export function Tooltip({ content, children, position = "top", className }: TooltipProps) {
  const [isVisible, setIsVisible] = useState(false);

  const positionClasses = {
    top: "-top-2 left-1/2 -translate-x-1/2 -translate-y-full mb-1",
    bottom: "-bottom-2 left-1/2 -translate-x-1/2 translate-y-full mt-1",
    left: "top-1/2 -left-2 -translate-x-full -translate-y-1/2 mr-1",
    right: "top-1/2 -right-2 translate-x-full -translate-y-1/2 ml-1",
  };

  return (
    <div
      className="relative inline-flex"
      onMouseEnter={() => setIsVisible(true)}
      onMouseLeave={() => setIsVisible(false)}
      onFocus={() => setIsVisible(true)}
      onBlur={() => setIsVisible(false)}
    >
      {children}
      {isVisible && (
        <div
          role="tooltip"
          className={cn(
            "absolute z-50 whitespace-nowrap rounded-md bg-slate-900 px-3 py-1.5 text-xs text-slate-100 shadow-md border border-white/10 animate-in fade-in duration-150 pointer-events-none",
            positionClasses[position],
            className
          )}
        >
          {content}
        </div>
      )}
    </div>
  );
}
