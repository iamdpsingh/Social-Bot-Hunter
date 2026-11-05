import React, { useState } from "react";
import { ChevronDown, ChevronUp, AlertCircle } from "lucide-react";
import { Card, CardHeader, CardTitle, CardContent } from "../ui/card";
import { EvidenceItemRow } from "./evidence-item-row";
import type { AccountAssessment, AccountEvidenceRecord } from "../../lib/api/types";

export interface EvidenceInspectorProps {
  assessment?: AccountAssessment | null;
  evidence?: AccountEvidenceRecord[] | any[];
}

export function EvidenceInspector({ assessment, evidence }: EvidenceInspectorProps) {
  const [isOpen, setIsOpen] = useState(true);
  const contributions = assessment?.contributions ?? (evidence || []).map((ev: any) => ({
    signal: ev.rule_name || ev.id || "Signal",
    weight: ev.weight ?? 0.25,
    value: ev.score ?? 0.8,
    description: ev.summary || "Observed heuristic indicator",
  }));

  return (
    <Card className="border-white/5 bg-slate-900/40" data-testid="evidence-inspector">
      <CardHeader
        className="cursor-pointer select-none py-4 px-6 flex flex-row items-center justify-between"
        onClick={() => setIsOpen(!isOpen)}
      >
        <div className="flex items-center gap-2">
          <AlertCircle className="h-4 w-4 text-amber-400" />
          <CardTitle className="text-sm font-semibold">Contributing Risk Signals & Evidence</CardTitle>
          <span className="rounded-full bg-white/10 px-2 py-0.5 text-[11px] font-mono text-muted-foreground">
            {contributions.length} signals
          </span>
        </div>
        <button
          type="button"
          aria-label="Toggle Evidence Details"
          aria-expanded={isOpen}
          aria-controls="evidence-content-panel"
          className="text-muted-foreground hover:text-foreground"
        >
          {isOpen ? <ChevronUp className="h-4 w-4" /> : <ChevronDown className="h-4 w-4" />}
        </button>
      </CardHeader>

      {isOpen && (
        <CardContent id="evidence-content-panel" role="region" aria-label="Evidence Signal List" className="px-6 pb-6 pt-0 space-y-3">
          {contributions.length === 0 ? (
            <p className="text-xs text-muted-foreground py-4 text-center">
              No heuristic rules triggered for this account.
            </p>
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
