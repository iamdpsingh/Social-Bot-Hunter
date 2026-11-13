import React from 'react';
import { PrivacyScanResponse } from '../../lib/types/security';
import { UserX, CheckCircle } from 'lucide-react';

interface Props {
  privacy: PrivacyScanResponse;
  onRescan?: () => void;
  isScanning?: boolean;
}

export function PrivacyAuditCard({ privacy, onRescan, isScanning }: Props) {
  return (
    <div className="rounded-xl border border-border bg-card p-5 shadow-sm">
      <div className="flex items-center justify-between pb-4 border-b border-border">
        <div className="flex items-center gap-2">
          <UserX className="h-5 w-5 text-purple-500" />
          <h3 className="font-semibold text-foreground">Privacy & PII Audit</h3>
        </div>
        <button
          onClick={onRescan}
          disabled={isScanning}
          className="text-xs px-3 py-1.5 rounded-lg bg-secondary text-secondary-foreground font-medium hover:opacity-90 disabled:opacity-50 transition"
        >
          {isScanning ? 'Auditing...' : 'Audit Datasets'}
        </button>
      </div>

      <div className="grid grid-cols-2 gap-3 my-4">
        <div className="rounded-lg bg-muted/30 p-3 text-center border border-border/40">
          <span className="text-xs text-muted-foreground block">Scanned Sources</span>
          <span className="text-lg font-mono font-semibold text-foreground">{privacy.scanned_sources}</span>
        </div>
        <div className={`rounded-lg p-3 text-center border ${privacy.passed ? 'bg-emerald-500/10 border-emerald-500/20 text-emerald-500' : 'bg-rose-500/10 border-rose-500/20 text-rose-500'}`}>
          <span className="text-xs block">PII Findings</span>
          <span className="text-lg font-mono font-semibold">{privacy.total_findings}</span>
        </div>
      </div>

      {privacy.findings.length === 0 ? (
        <div className="flex items-center gap-2 p-3 rounded-lg bg-emerald-500/5 border border-emerald-500/20 text-xs text-emerald-600 dark:text-emerald-400">
          <CheckCircle className="h-4 w-4 shrink-0" />
          <span>Strict data minimization verified: zero un-fingerprinted PII in storage.</span>
        </div>
      ) : (
        <div className="space-y-2">
          {privacy.findings.map((f, idx) => (
            <div
              key={`${f.pii_type}-${idx}`}
              className="flex items-center justify-between text-xs p-2 rounded bg-muted/20 border border-border/40 font-mono"
            >
              <span className="font-semibold text-purple-500">{f.pii_type}</span>
              <span className="text-muted-foreground">{f.location}:{f.line_number}</span>
              <span className="text-foreground">{f.masked_value}</span>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
