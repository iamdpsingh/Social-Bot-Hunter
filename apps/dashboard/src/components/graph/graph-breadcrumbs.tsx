"use client";

import Link from "next/link";
import React from "react";

export interface GraphBreadcrumbsProps {
  scanId: string;
  activeNodeId?: string | null;
}

export function GraphBreadcrumbs({ scanId, activeNodeId }: GraphBreadcrumbsProps) {
  return (
    <nav aria-label="Investigation graph navigation" className="text-xs text-slate-400 flex items-center gap-1.5">
      <Link href="/investigations" className="hover:text-slate-200">
        Investigations
      </Link>
      <span>/</span>
      <Link href={`/investigations/${scanId}`} className="hover:text-slate-200 font-mono">
        {scanId}
      </Link>
      <span>/</span>
      <span className="text-slate-200 font-medium">Network Explorer</span>
      {activeNodeId && (
        <>
          <span>/</span>
          <span className="text-blue-400 font-mono">{activeNodeId}</span>
        </>
      )}
    </nav>
  );
}
