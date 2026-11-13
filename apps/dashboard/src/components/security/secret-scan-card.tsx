import React from 'react';
import { SecretScanResponse } from '../../lib/types/security';
import { KeyRound, CheckCircle2 } from 'lucide-react';

interface Props {
  scan: SecretScanResponse;
  onRescan?: () => void;
  isScanning?: boolean;
}

export function SecretScanCard({ scan, onRescan, isScanning }: Props) {
  return (
    <div className="rounded-xl border border-border bg-card p-5 shadow-sm">
      <div className="flex items-center justify-between pb-4 border-b border-border">
        <div className="flex items-center gap-2">
          <KeyRound className="h-5 w-5 text-indigo-500" />
          <h3 className="font-semibold text-foreground">Hardcoded Secret Scanner</h3>
        </div>
        <button
          onClick={onRescan}
          disabled={isScanning}
          className="text-xs px-3 py-1.5 rounded-lg bg-primary text-primary-foreground font-medium hover:opacity-90 disabled:opacity-50 transition"
        >
          {isScanning ? 'Scanning...' : 'Scan Now'}
        </button>
      </div>

      <div className="mt-4">
        {scan.findings.length === 0 ? (
          <div className="flex flex-col items-center justify-center p-6 text-center rounded-lg bg-emerald-500/5 border border-emerald-500/20">
            <CheckCircle2 className="h-8 w-8 text-emerald-500 mb-2" />
            <p className="text-sm font-medium text-emerald-600 dark:text-emerald-400">
              Zero hardcoded secrets detected
            </p>
            <p className="text-xs text-muted-foreground mt-1">
              Scanned directory: <span className="font-mono">{scan.target_dir}</span>
            </p>
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-xs text-left">
              <thead>
                <tr className="border-b border-border text-muted-foreground font-mono">
                  <th className="py-2">Rule</th>
                  <th className="py-2">Severity</th>
                  <th className="py-2">Location</th>
                  <th className="py-2">Masked Secret</th>
                  <th className="py-2">Entropy</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-border/40 font-mono">
                {scan.findings.map((f, idx) => (
                  <tr key={`${f.rule_id}-${idx}`} className="hover:bg-muted/30">
                    <td className="py-2 font-medium text-foreground">{f.rule_name}</td>
                    <td className="py-2">
                      <span className="px-1.5 py-0.5 rounded text-[10px] bg-rose-500/10 text-rose-500 font-semibold">
                        {f.severity}
                      </span>
                    </td>
                    <td className="py-2 text-muted-foreground">
                      {f.file_path}:{f.line_number}
                    </td>
                    <td className="py-2 text-foreground font-bold">{f.masked_value}</td>
                    <td className="py-2 text-muted-foreground">{f.entropy.toFixed(2)}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
}
