import React, { useState } from 'react';
import type { DatabaseBackup, RuntimeStatus, StorageStats, WorkerJob } from '@/lib/types/runtime';
import { ProcessSupervisorCard } from './process-supervisor-card';
import { WorkerQueueCard } from './worker-queue-card';
import { StorageBreakdownCard } from './storage-breakdown-card';
import { DatabaseBackupPanel } from './database-backup-panel';

interface RuntimeOrchestrationViewProps {
  runtimeStatus: RuntimeStatus;
  workerJobs: WorkerJob[];
  storageStats: StorageStats;
  backups: DatabaseBackup[];
  onRefresh?: () => void;
  onEnqueueJob?: (taskType: string) => void;
  onPruneStorage?: () => void;
  onCreateBackup?: () => void;
  onVerifyBackup?: (backupId: string) => void;
}

export function RuntimeOrchestrationView({
  runtimeStatus,
  workerJobs,
  storageStats,
  backups,
  onRefresh,
  onEnqueueJob,
  onPruneStorage,
  onCreateBackup,
  onVerifyBackup,
}: RuntimeOrchestrationViewProps) {
  const [activeTab, setActiveTab] = useState<'supervisor' | 'worker' | 'storage' | 'backups'>('supervisor');

  return (
    <div className="space-y-6" data-testid="runtime-orchestration-view">
      <div className="flex border-b border-slate-800 space-x-4">
        <button
          onClick={() => setActiveTab('supervisor')}
          className={`pb-2.5 text-sm font-medium border-b-2 transition ${
            activeTab === 'supervisor'
              ? 'border-indigo-500 text-indigo-400'
              : 'border-transparent text-slate-400 hover:text-slate-200'
          }`}
        >
          Processes & Hardware
        </button>
        <button
          onClick={() => setActiveTab('worker')}
          className={`pb-2.5 text-sm font-medium border-b-2 transition ${
            activeTab === 'worker'
              ? 'border-indigo-500 text-indigo-400'
              : 'border-transparent text-slate-400 hover:text-slate-200'
          }`}
        >
          Worker Queue
        </button>
        <button
          onClick={() => setActiveTab('storage')}
          className={`pb-2.5 text-sm font-medium border-b-2 transition ${
            activeTab === 'storage'
              ? 'border-indigo-500 text-indigo-400'
              : 'border-transparent text-slate-400 hover:text-slate-200'
          }`}
        >
          Storage & Retention
        </button>
        <button
          onClick={() => setActiveTab('backups')}
          className={`pb-2.5 text-sm font-medium border-b-2 transition ${
            activeTab === 'backups'
              ? 'border-indigo-500 text-indigo-400'
              : 'border-transparent text-slate-400 hover:text-slate-200'
          }`}
        >
          Database Backups
        </button>
      </div>

      {activeTab === 'supervisor' && (
        <ProcessSupervisorCard status={runtimeStatus} onRefresh={onRefresh} />
      )}

      {activeTab === 'worker' && (
        <WorkerQueueCard jobs={workerJobs} queueStats={runtimeStatus.queue} onEnqueueJob={onEnqueueJob} />
      )}

      {activeTab === 'storage' && (
        <StorageBreakdownCard stats={storageStats} onPrune={onPruneStorage} />
      )}

      {activeTab === 'backups' && (
        <DatabaseBackupPanel
          backups={backups}
          onCreateBackup={onCreateBackup}
          onVerifyBackup={onVerifyBackup}
        />
      )}
    </div>
  );
}
