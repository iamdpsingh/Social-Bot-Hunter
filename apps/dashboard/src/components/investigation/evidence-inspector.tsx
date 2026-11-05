import React, { useState } from "react";
import { ChevronDown, ChevronUp, AlertCircle, Info } from "lucide-react";
import { Card, CardHeader, CardTitle, CardContent } from "../ui/card";
import { EvidenceItemRow } from "./evidence-item-row";
import type { AccountAssessment } from "../../lib/api/types";

export interface EvidenceInspectorProps {
  assessment?: AccountAssessment | null;
}

export function EvidenceInspector({ assessment }: EvidenceInspectorProps) {
  const [isOpen, setIsOpen] = useState(true);
  const contributions = assessment?.contributions || [];

  return (
    <Card className="border-white/5 bg-slate-900/40">
      <CardHeader className="cursor-pointer select-none py-4 px-6 flex flex-row items-center justify-between" onClick={() => setIsOpen(!isOpen)}>
        <div className="flex items-center gap-2">
          <AlertCircle className="h-4 w-4 text-amber-400" />
          <CardTitle className="text-sm font-semibold">Contributing Risk Signals & Evidence</CardTitle>
          <span className="rounded-full bg-white/10 px-2 py-0.5 text-[11px] font-mono text-muted-foreground">
            {contributions.length} signals
          </span>
        </div>
        <button type="button" aria-label="Toggle Evidence" className="text-muted-foreground hover:text-foreground">
          {isOpen ? <ChevronUp className="h-4 w-4" /> : <ChevronDown className="h-4 w-4" />}
        </button>
      </CardHeader>

      {isOpen && (
        <CardContent className="px-6 pb-6 pt-0 space-y-3">
          {contributions.length === 0 ? (
            <div className="flex items-center gap-2 p-4 text-xs text-muted-foreground bg-white/5 rounded-lg">
              <Info className="h-4 w-4" />
              <span>No heuristic risk indicators triggered for this account.</span>
            </div>
          ) : (
            <div className="divide-y divide-white/5">
              {contributions.map((signal, idx) => (
                <EvidenceItemRow key={idx} signal={signal} />
              ))}
            </div>
          )}
        </CardContent>
      )}
    </Card>
  );
}
