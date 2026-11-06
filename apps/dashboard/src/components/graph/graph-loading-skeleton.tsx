"use client";

import React from "react";

export function GraphLoadingSkeleton() {
  return (
    <div
      data-testid="graph-loading-skeleton"
      className="flex flex-col items-center justify-center min-h-[500px] w-full bg-slate-950/80 rounded-lg border border-slate-800 animate-pulse p-6"
    >
      <div className="w-16 h-16 rounded-full border-2 border-slate-700 border-t-blue-500 animate-spin mb-4" />
      <p className="text-xs text-slate-400 font-medium">Constructing graph elements & running layout engine...</p>
    </div>
  );
}
