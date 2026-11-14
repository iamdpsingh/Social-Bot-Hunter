import React from 'react';
import { CheckCircle2, AlertTriangle, ShieldCheck } from 'lucide-react';
import { SystemReadinessScorecard } from '../../lib/types/acceptance';

interface Props {
  scorecard: SystemReadinessScorecard;
}

export function ReadinessScorecard({ scorecard }: Props) {
  const isReady = scorecard.overallStatus === 'PRODUCTION_READY';

  return (
    <div className="rounded-xl border border-border bg-card p-6 shadow-sm">
      <div className="flex items-center justify-between pb-4 border-b border-border">
        <div className="flex items-center gap-3">
          <ShieldCheck className="h-7 w-7 text-emerald-500" />
          <div>
            <h2 className="text-lg font-bold text-foreground">Production Readiness Scorecard</h2>
            <p className="text-xs text-muted-foreground">Specification Section 19 Acceptance Criteria</p>
          </div>
        </div>
        <div className="flex items-center gap-2">
          <span
            className={`inline-flex items-center px-3 py-1 rounded-full text-xs font-semibold border ${
              isReady
                ? 'bg-emerald-500/10 text-emerald-500 border-emerald-500/30'
                : 'bg-amber-500/10 text-amber-500 border-amber-500/30'
            }`}
          >
            {isReady ? 'PRODUCTION READY' : 'DEGRADED'}
          </span>
          <span className="text-xl font-extrabold text-foreground">{scorecard.compliancePercentage}%</span>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-3 mt-4">
        {scorecard.criteria.map((c) => (
          <div key={c.id} className="p-3 rounded-lg border border-border bg-muted/30 flex items-start gap-3">
            {c.verified ? (
              <CheckCircle2 className="h-5 w-5 text-emerald-500 shrink-0 mt-0.5" />
            ) : (
              <AlertTriangle className="h-5 w-5 text-amber-500 shrink-0 mt-0.5" />
            )}
            <div>
              <div className="flex items-center gap-2">
                <span className="text-xs font-mono font-bold text-primary">{c.section}</span>
                <span className="text-sm font-semibold text-foreground">{c.title}</span>
              </div>
              <p className="text-xs text-muted-foreground mt-0.5">{c.description}</p>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
