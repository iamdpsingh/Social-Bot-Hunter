"use client";

import React, { useState } from "react";

export interface NeighborExpandModalProps {
  nodeId: string;
  isOpen: boolean;
  onClose: () => void;
  onExpand: (direction: "in" | "out" | "both", radius: number) => void;
}

export function NeighborExpandModal({
  nodeId,
  isOpen,
  onClose,
  onExpand,
}: NeighborExpandModalProps) {
  const [direction, setDirection] = useState<"in" | "out" | "both">("both");
  const [radius, setRadius] = useState<number>(1);

  if (!isOpen) return null;

  return (
    <div
      data-testid="neighbor-expand-modal"
      className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 backdrop-blur-sm"
      role="dialog"
      aria-modal="true"
      aria-labelledby="expand-modal-title"
    >
      <div className="bg-slate-900 border border-slate-700 p-5 rounded-xl max-w-sm w-full mx-4 shadow-2xl text-slate-200">
        <h3 id="expand-modal-title" className="font-semibold text-base mb-1">
          Expand Ego Network
        </h3>
        <p className="text-xs text-slate-400 mb-4 font-mono truncate">Node: {nodeId}</p>

        <div className="space-y-3 mb-5 text-xs">
          <div>
            <label className="block text-slate-300 font-medium mb-1">Direction</label>
            <div className="grid grid-cols-3 gap-1.5">
              {(["both", "in", "out"] as const).map((d) => (
                <button
                  key={d}
                  type="button"
                  onClick={() => setDirection(d)}
                  className={`py-1.5 rounded font-medium capitalize border transition ${
                    direction === d
                      ? "bg-blue-600 text-white border-blue-500"
                      : "bg-slate-800 text-slate-300 border-slate-700 hover:bg-slate-700"
                  }`}
                >
                  {d}
                </button>
              ))}
            </div>
          </div>

          <div>
            <label className="block text-slate-300 font-medium mb-1">Hop Depth (Radius)</label>
            <div className="grid grid-cols-2 gap-1.5">
              {[1, 2].map((r) => (
                <button
                  key={r}
                  type="button"
                  onClick={() => setRadius(r)}
                  className={`py-1.5 rounded font-medium border transition ${
                    radius === r
                      ? "bg-blue-600 text-white border-blue-500"
                      : "bg-slate-800 text-slate-300 border-slate-700 hover:bg-slate-700"
                  }`}
                >
                  {r} Hop{r > 1 ? "s" : ""}
                </button>
              ))}
            </div>
          </div>
        </div>

        <div className="flex gap-2">
          <button
            type="button"
            onClick={onClose}
            className="flex-1 py-1.5 text-xs rounded bg-slate-800 hover:bg-slate-700 text-slate-300 transition"
          >
            Cancel
          </button>
          <button
            type="button"
            onClick={() => {
              onExpand(direction, radius);
              onClose();
            }}
            className="flex-1 py-1.5 text-xs rounded bg-blue-600 hover:bg-blue-500 text-white font-medium transition"
          >
            Apply Expansion
          </button>
        </div>
      </div>
    </div>
  );
}
