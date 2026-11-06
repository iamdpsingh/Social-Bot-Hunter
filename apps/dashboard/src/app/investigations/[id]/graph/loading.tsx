import React from "react";
import { GraphLoadingSkeleton } from "../../../../components/graph/graph-loading-skeleton";

export default function Loading() {
  return (
    <div className="p-6 max-w-7xl mx-auto space-y-4">
      <div className="h-6 w-48 bg-slate-800 rounded animate-pulse" />
      <GraphLoadingSkeleton />
    </div>
  );
}
