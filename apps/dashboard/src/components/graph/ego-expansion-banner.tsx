"use client";

import React from "react";

export interface EgoExpansionBannerProps {
  centerNodeId: string;
  radius: number;
  onResetExpansion: () => void;
}

export function EgoExpansionBanner({
  centerNodeId,
  radius,
  onResetExpansion,
}: EgoExpansionBannerProps) {
  return (
    <div
      data-testid="ego-expansion-banner"
      className="flex items-center justify-between p-2.5 bg-blue-950/40 border border-blue-800/80 rounded-lg text-blue-200 text-xs"
    >
      <div className="flex items-center gap-2">
        <span className="w-2 h-2 rounded-full bg-blue-400 animate-pulse" />
        <span>
          Ego-expansion active around <strong className="font-mono text-white">{centerNodeId}</strong> ({radius} hop{radius > 1 ? "s" : ""})
        </span>
      </div>
      <button
        type="button"
        onClick={onResetExpansion}
        className="text-xs text-blue-300 hover:text-white underline font-medium"
      >
        Reset Expansion
      </button>
    </div>
  );
}
