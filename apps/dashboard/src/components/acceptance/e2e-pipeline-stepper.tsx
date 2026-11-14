import React from 'react';
import { ArrowRight, CheckCircle2 } from 'lucide-react';

interface Step {
  id: string;
  name: string;
  detail: string;
  status: 'COMPLETED' | 'ACTIVE' | 'PENDING';
}

const DEFAULT_STEPS: Step[] = [
  { id: '1', name: 'Ingestion', detail: 'URL probe or batch import', status: 'COMPLETED' },
  { id: '2', name: 'Extraction', detail: 'Profile & signal extraction', status: 'COMPLETED' },
  { id: '3', name: 'Detection', detail: 'Heuristic + ML scoring', status: 'COMPLETED' },
  { id: '4', name: 'Coordination', detail: 'SimHash & burst clustering', status: 'COMPLETED' },
  { id: '5', name: 'Network Graph', detail: 'Cytoscape.js visualization', status: 'COMPLETED' },
];

interface Props {
  steps?: Step[];
}

export function E2EPipelineStepper({ steps = DEFAULT_STEPS }: Props) {
  return (
    <div className="rounded-xl border border-border bg-card p-6 shadow-sm">
      <h2 className="text-lg font-bold text-foreground mb-1">End-to-End Pipeline Verification</h2>
      <p className="text-xs text-muted-foreground mb-6">Live execution path through detection and graph layers</p>

      <div className="flex flex-col md:flex-row items-center justify-between gap-3">
        {steps.map((step, idx) => (
          <React.Fragment key={step.id}>
            <div className="flex-1 p-3 rounded-lg border border-border bg-muted/20 text-center w-full">
              <div className="flex items-center justify-center gap-1.5 mb-1 text-emerald-500">
                <CheckCircle2 className="h-4 w-4" />
                <span className="text-xs font-bold uppercase">{step.name}</span>
              </div>
              <p className="text-xs text-muted-foreground">{step.detail}</p>
            </div>
            {idx < steps.length - 1 && (
              <ArrowRight className="h-4 w-4 text-muted-foreground shrink-0 hidden md:block" />
            )}
          </React.Fragment>
        ))}
      </div>
    </div>
  );
}
