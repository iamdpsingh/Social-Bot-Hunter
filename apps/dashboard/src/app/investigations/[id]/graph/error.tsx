"use client";

import React from "react";

export default function ErrorBoundary({
  error,
  reset,
}: {
  error: Error & { digest?: string };
  reset: () => void;
}) {
  return (
    <div className="p-8 max-w-xl mx-auto text-center space-y-4">
      <h2 className="text-lg font-bold text-red-400">Failed to load network graph</h2>
      <p className="text-xs text-slate-400">{error.message || "An unexpected error occurred."}</p>
      <button
        type="button"
        onClick={() => reset()}
        className="px-4 py-2 bg-blue-600 hover:bg-blue-500 rounded text-xs font-semibold text-white transition"
      >
        Retry Loading
      </button>
    </div>
  );
}
