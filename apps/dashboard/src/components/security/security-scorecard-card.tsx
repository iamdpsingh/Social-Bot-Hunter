import React from 'react';
import { SecurityScorecardResponse } from '../../lib/types/security';
import { ShieldCheck, ShieldAlert } from 'lucide-react';

interface Props {
  scorecard: SecurityScorecardResponse;
}

export function SecurityScorecardCard({ scorecard }: Props) {
  const grade = scorecard.passed_audit ? 'A' : scorecard.failed_checks === 1 ? 'B' : 'F';
  const gradeColor =
    grade === 'A'
      ? 'text-emerald-500 border-emerald-500/30 bg-emerald-500/10'
      : grade === 'B'
      ? 'text-amber-500 border-amber-500/30 bg-amber-500/10'
      : 'text-rose-500 border-rose-500/30 bg-rose-500/10';

  return (
    <div className="rounded-xl border border-border bg-card p-5 shadow-sm">
      <div className="flex items-center justify-between pb-4 border-b border-border">
        <div className="flex items-center gap-3">
          {scorecard.passed_audit ? (
            <ShieldCheck className="h-6 w-6 text-emerald-500" />
          ) : (
            <ShieldAlert className="h-6 w-6 text-rose-500" />
          )}
          <div>
            <h3 className="font-semibold text-foreground">Security Audit Scorecard</h3>
            <p className="text-xs text-muted-foreground">Automated local and repository posture verification</p>
          </div>
        </div>
        <div className={`px-4 py-1.5 rounded-lg border font-mono text-xl font-bold ${gradeColor}`}>
          Grade {grade}
        </div>
      </div>

      <div className="grid grid-cols-3 gap-3 my-4">
        <div className="rounded-lg bg-muted/40 p-3 text-center border border-border/50">
          <span className="text-xs text-muted-foreground block">Total Checks</span>
          <span className="text-lg font-mono font-semibold text-foreground">{scorecard.total_checks}</span>
        </div>
        <div className="rounded-lg bg-emerald-500/10 p-3 text-center border border-emerald-500/20">
          <span className="text-xs text-emerald-600 dark:text-emerald-400 block">Passed</span>
          <span className="text-lg font-mono font-semibold text-emerald-600 dark:text-emerald-400">
            {scorecard.passed_checks}
          </span>
        </div>
        <div className="rounded-lg bg-rose-500/10 p-3 text-center border border-rose-500/20">
          <span className="text-xs text-rose-600 dark:text-rose-400 block">Failed</span>
          <span className="text-lg font-mono font-semibold text-rose-600 dark:text-rose-400">
            {scorecard.failed_checks}
          </span>
        </div>
      </div>

      <div className="space-y-2 mt-4">
        {scorecard.checks.map((chk) => (
          <div
            key={chk.check_id}
            className="flex items-center justify-between text-xs p-2 rounded-md bg-muted/20 border border-border/40"
          >
            <div className="flex items-center gap-2">
              <span
                className={`h-2 w-2 rounded-full ${chk.passed ? 'bg-emerald-500' : 'bg-rose-500'}`}
              />
              <span className="font-medium text-foreground">{chk.name}</span>
            </div>
            <span
              className={`font-mono px-2 py-0.5 rounded text-[10px] ${
                chk.passed
                  ? 'bg-emerald-500/10 text-emerald-500'
                  : 'bg-rose-500/10 text-rose-500 font-semibold'
              }`}
            >
              {chk.passed ? 'PASS' : `FAIL (${chk.findings_count})`}
            </span>
          </div>
        ))}
      </div>
    </div>
  );
}
