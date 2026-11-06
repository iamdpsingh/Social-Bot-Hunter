"use client";

import Link from "next/link";
import React, { useMemo, useState } from "react";
import type { CytoscapeGraphElements } from "../../lib/api/types";
import { GRAPH_NODE_COLORS } from "../../tokens/graph";

export interface AccessibleGraphTableProps {
  scanId: string;
  elements: CytoscapeGraphElements;
  onSelectNode?: (nodeId: string) => void;
  selectedNodeId?: string | null;
}

export function AccessibleGraphTable({
  scanId,
  elements,
  onSelectNode,
  selectedNodeId,
}: AccessibleGraphTableProps) {
  const [sortField, setSortField] = useState<"score" | "id" | "inDegree" | "outDegree">("score");
  const [sortAsc, setSortAsc] = useState(false);
  const [page, setPage] = useState(1);
  const pageSize = 20;

  // Compute in/out degree per node
  const degreeMap = useMemo(() => {
    const inDeg: Record<string, number> = {};
    const outDeg: Record<string, number> = {};

    elements.edges.forEach((e) => {
      outDeg[e.data.source] = (outDeg[e.data.source] || 0) + 1;
      inDeg[e.data.target] = (inDeg[e.data.target] || 0) + 1;
    });

    return { inDeg, outDeg };
  }, [elements.edges]);

  const sortedNodes = useMemo(() => {
    return [...elements.nodes].sort((a, b) => {
      let valA: any;
      let valB: any;

      if (sortField === "score") {
        valA = a.data.score ?? -1;
        valB = b.data.score ?? -1;
      } else if (sortField === "inDegree") {
        valA = degreeMap.inDeg[a.data.id] || 0;
        valB = degreeMap.inDeg[b.data.id] || 0;
      } else if (sortField === "outDegree") {
        valA = degreeMap.outDeg[a.data.id] || 0;
        valB = degreeMap.outDeg[b.data.id] || 0;
      } else {
        valA = a.data.id;
        valB = b.data.id;
      }

      if (valA < valB) return sortAsc ? -1 : 1;
      if (valA > valB) return sortAsc ? 1 : -1;
      return 0;
    });
  }, [elements.nodes, sortField, sortAsc, degreeMap]);

  const totalPages = Math.max(1, Math.ceil(sortedNodes.length / pageSize));
  const pageNodes = sortedNodes.slice((page - 1) * pageSize, page * pageSize);

  const handleSort = (field: typeof sortField) => {
    if (sortField === field) {
      setSortAsc(!sortAsc);
    } else {
      setSortField(field);
      setSortAsc(false);
    }
  };

  return (
    <div
      data-testid="accessible-graph-table"
      className="w-full bg-slate-900 border border-slate-800 rounded-lg overflow-hidden text-xs"
      role="region"
      aria-label="Accessible network accounts table"
    >
      <div className="overflow-x-auto">
        <table className="w-full text-left text-slate-300">
          <thead className="bg-slate-950/80 text-slate-400 border-b border-slate-800 uppercase text-[10px] tracking-wider">
            <tr>
              <th
                scope="col"
                className="py-3 px-4 cursor-pointer hover:text-slate-200"
                onClick={() => handleSort("id")}
              >
                Account / Node ID {sortField === "id" && (sortAsc ? "▲" : "▼")}
              </th>
              <th scope="col" className="py-3 px-4">
                Classification
              </th>
              <th
                scope="col"
                className="py-3 px-4 cursor-pointer hover:text-slate-200"
                onClick={() => handleSort("score")}
              >
                Risk Score {sortField === "score" && (sortAsc ? "▲" : "▼")}
              </th>
              <th
                scope="col"
                className="py-3 px-4 cursor-pointer hover:text-slate-200"
                onClick={() => handleSort("inDegree")}
              >
                In-Degree (Followers) {sortField === "inDegree" && (sortAsc ? "▲" : "▼")}
              </th>
              <th
                scope="col"
                className="py-3 px-4 cursor-pointer hover:text-slate-200"
                onClick={() => handleSort("outDegree")}
              >
                Out-Degree (Following) {sortField === "outDegree" && (sortAsc ? "▲" : "▼")}
              </th>
              <th scope="col" className="py-3 px-4">
                Cluster
              </th>
              <th scope="col" className="py-3 px-4 text-right">
                Actions
              </th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-800/60 font-mono">
            {pageNodes.map((n) => {
              const band = n.data.band || "insufficient_evidence";
              const colors = GRAPH_NODE_COLORS[band] || GRAPH_NODE_COLORS.insufficient_evidence;
              const isSelected = n.data.id === selectedNodeId;

              return (
                <tr
                  key={n.data.id}
                  className={`hover:bg-slate-800/40 transition cursor-pointer ${
                    isSelected ? "bg-blue-950/40 border-l-2 border-blue-500" : ""
                  }`}
                  onClick={() => onSelectNode?.(n.data.id)}
                >
                  <td className="py-3 px-4 font-semibold text-slate-200">
                    <div>{n.data.label || n.data.id}</div>
                    <div className="text-[10px] text-slate-500 font-normal">{n.data.id}</div>
                  </td>
                  <td className="py-3 px-4">
                    <span
                      className="px-2 py-0.5 rounded text-[10px] font-sans font-medium capitalize"
                      style={{
                        backgroundColor: `${colors.bg}22`,
                        color: colors.bg,
                        border: `1px solid ${colors.border}44`,
                      }}
                    >
                      {band.replace("_", " ")}
                    </span>
                  </td>
                  <td className="py-3 px-4">
                    <div className="flex items-center gap-2">
                      <div className="w-16 bg-slate-800 h-1.5 rounded-full overflow-hidden">
                        <div
                          className="h-full rounded-full"
                          style={{
                            width: `${(n.data.score || 0) * 100}%`,
                            backgroundColor: colors.bg,
                          }}
                        />
                      </div>
                      <span>{n.data.score != null ? `${Math.round(n.data.score * 100)}%` : "N/A"}</span>
                    </div>
                  </td>
                  <td className="py-3 px-4">{degreeMap.inDeg[n.data.id] || 0}</td>
                  <td className="py-3 px-4">{degreeMap.outDeg[n.data.id] || 0}</td>
                  <td className="py-3 px-4">
                    {n.data.cluster_id ? (
                      <span className="px-2 py-0.5 rounded bg-purple-900/40 text-purple-300 text-[10px]">
                        {n.data.cluster_id}
                      </span>
                    ) : (
                      <span className="text-slate-600">-</span>
                    )}
                  </td>
                  <td className="py-3 px-4 text-right font-sans">
                    <Link
                      href={`/investigations/${scanId}/accounts/${n.data.id}`}
                      className="text-blue-400 hover:text-blue-300 underline font-medium"
                      onClick={(e) => e.stopPropagation()}
                    >
                      Profile &rarr;
                    </Link>
                  </td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>

      <div className="flex items-center justify-between px-4 py-3 bg-slate-950/60 border-t border-slate-800 text-slate-400">
        <span>
          Showing {(page - 1) * pageSize + 1} - {Math.min(page * pageSize, sortedNodes.length)} of {sortedNodes.length} nodes
        </span>
        <div className="flex gap-2">
          <button
            type="button"
            disabled={page <= 1}
            onClick={() => setPage((p) => p - 1)}
            className="px-2.5 py-1 rounded bg-slate-800 hover:bg-slate-700 disabled:opacity-40 disabled:cursor-not-allowed text-slate-200"
          >
            Previous
          </button>
          <span className="px-2 py-1">
            Page {page} of {totalPages}
          </span>
          <button
            type="button"
            disabled={page >= totalPages}
            onClick={() => setPage((p) => p + 1)}
            className="px-2.5 py-1 rounded bg-slate-800 hover:bg-slate-700 disabled:opacity-40 disabled:cursor-not-allowed text-slate-200"
          >
            Next
          </button>
        </div>
      </div>
    </div>
  );
}
