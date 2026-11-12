import React from 'react';
import type { DatabaseBackup } from '@/lib/types/runtime';

interface DatabaseBackupPanelProps {
  backups: DatabaseBackup[];
  onCreateBackup?: () => void;
  onVerifyBackup?: (backupId: string) => void;
  creating?: boolean;
}

export function DatabaseBackupPanel({
  backups,
  onCreateBackup,
  onVerifyBackup,
  creating,
}: DatabaseBackupPanelProps) {
  return (
    <div className="bg-slate-900 border border-slate-800 rounded-xl p-5 shadow-lg" data-testid="database-backup-panel">
      <div className="flex items-center justify-between mb-4">
        <div>
          <h3 className="text-base font-semibold text-slate-100">Database Backups & Recovery</h3>
          <p className="text-xs text-slate-400">Atomic VACUUM INTO snapshots with SHA-256 verification</p>
        </div>
        {onCreateBackup && (
          <button
            onClick={onCreateBackup}
            disabled={creating}
            className="px-3 py-1.5 text-xs font-semibold text-emerald-400 bg-emerald-500/10 border border-emerald-500/30 rounded-lg hover:bg-emerald-500/20 transition disabled:opacity-50"
          >
            {creating ? 'Creating...' : '+ Create Backup'}
          </button>
        )}
      </div>

      <div className="overflow-x-auto">
        <table className="w-full text-left text-xs text-slate-300">
          <thead className="bg-slate-800/70 text-slate-400 uppercase">
            <tr>
              <th className="p-2.5">Backup ID</th>
              <th className="p-2.5">Engine</th>
              <th className="p-2.5">Size</th>
              <th className="p-2.5">Tables</th>
              <th className="p-2.5">Created</th>
              <th className="p-2.5">Action</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-800">
            {backups.length === 0 ? (
              <tr>
                <td colSpan={6} className="p-4 text-center text-slate-500">
                  No database backups recorded
                </td>
              </tr>
            ) : (
              backups.map((b) => (
                <tr key={b.backup_id} className="hover:bg-slate-800/40">
                  <td className="p-2.5 font-mono text-slate-200">
                    <div>{b.filename}</div>
                    <div className="text-[10px] text-slate-500 truncate max-w-xs">{b.sha256}</div>
                  </td>
                  <td className="p-2.5 uppercase text-slate-400">{b.database_type}</td>
                  <td className="p-2.5 font-mono">{(b.size_bytes / 1024).toFixed(1)} KB</td>
                  <td className="p-2.5">{Object.keys(b.table_counts).length} tables</td>
                  <td className="p-2.5 text-slate-400">{new Date(b.created_at).toLocaleString()}</td>
                  <td className="p-2.5">
                    {onVerifyBackup && (
                      <button
                        onClick={() => onVerifyBackup(b.backup_id)}
                        className="px-2 py-0.5 text-xs font-medium text-slate-300 bg-slate-800 hover:bg-slate-700 rounded border border-slate-700 transition"
                      >
                        Verify
                      </button>
                    )}
                  </td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
}
