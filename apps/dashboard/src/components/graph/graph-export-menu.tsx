"use client";

import React, { useState } from "react";

export interface GraphExportMenuProps {
  onExportPng: () => void;
  onExportJson: () => void;
}

export function GraphExportMenu({ onExportPng, onExportJson }: GraphExportMenuProps) {
  const [open, setOpen] = useState(false);

  return (
    <div className="relative inline-block text-left" data-testid="graph-export-menu">
      <button
        type="button"
        onClick={() => setOpen(!open)}
        className="px-2.5 py-1 text-xs font-medium rounded bg-slate-800 text-slate-200 hover:bg-slate-700 border border-slate-700 transition"
        aria-haspopup="true"
        aria-expanded={open}
      >
        Export &darr;
      </button>

      {open && (
        <div
          className="absolute right-0 mt-1 w-44 rounded-md shadow-lg bg-slate-800 border border-slate-700 ring-1 ring-black ring-opacity-5 z-30 py-1"
          role="menu"
        >
          <button
            type="button"
            onClick={() => {
              setOpen(false);
              onExportPng();
            }}
            className="w-full text-left px-3 py-1.5 text-xs text-slate-200 hover:bg-slate-700 transition"
            role="menuitem"
          >
            Export Canvas (PNG)
          </button>
          <button
            type="button"
            onClick={() => {
              setOpen(false);
              onExportJson();
            }}
            className="w-full text-left px-3 py-1.5 text-xs text-slate-200 hover:bg-slate-700 transition"
            role="menuitem"
          >
            Export Graph (JSON)
          </button>
        </div>
      )}
    </div>
  );
}
