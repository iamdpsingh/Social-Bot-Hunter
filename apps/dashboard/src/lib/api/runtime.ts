import { apiGet, apiPost } from './client';
import type {
  DatabaseBackup,
  EnvCheckReport,
  RuntimeStatus,
  StorageStats,
  WorkerJob,
} from '../types/runtime';

export async function fetchRuntimeStatus(): Promise<RuntimeStatus> {
  return apiGet<RuntimeStatus>('/api/v1/runtime/status');
}

export async function fetchEnvCheck(noPorts: boolean = false): Promise<EnvCheckReport> {
  return apiGet<EnvCheckReport>(`/api/v1/runtime/env?no_ports=${noPorts}`);
}

export async function fetchWorkerJobs(status?: string, limit: number = 50): Promise<WorkerJob[]> {
  const query = status ? `?status=${status}&limit=${limit}` : `?limit=${limit}`;
  return apiGet<WorkerJob[]>(`/api/v1/runtime/worker/jobs${query}`);
}

export async function enqueueWorkerJob(
  taskType: string,
  payload: Record<string, any> = {},
  priority: number = 10
): Promise<{ job_id: string; status: string }> {
  return apiPost('/api/v1/runtime/worker/jobs', {
    task_type: taskType,
    payload,
    priority,
  });
}

export async function fetchStorageStats(): Promise<StorageStats> {
  return apiGet<StorageStats>('/api/v1/storage/stats');
}

export async function triggerStoragePrune(options: {
  category?: string;
  maxAgeDays?: number;
  maxSizeMb?: number;
  dryRun?: boolean;
} = {}): Promise<any> {
  return apiPost('/api/v1/storage/prune', {
    category: options.category,
    max_age_days: options.maxAgeDays ?? 30,
    max_size_mb: options.maxSizeMb,
    dry_run: options.dryRun ?? false,
  });
}

export async function fetchDatabaseBackups(): Promise<DatabaseBackup[]> {
  const res = await apiGet<{ backups: DatabaseBackup[] }>('/api/v1/storage/backups');
  return res.backups;
}

export async function createDatabaseBackup(options: {
  compress?: boolean;
  notes?: string;
} = {}): Promise<DatabaseBackup> {
  return apiPost<DatabaseBackup>('/api/v1/storage/backups', {
    compress: options.compress ?? false,
    notes: options.notes,
  });
}

export async function verifyDatabaseBackup(backupId: string): Promise<{
  backup_id: string;
  is_valid: boolean;
  message: string;
}> {
  return apiPost('/api/v1/storage/backups/verify', { backup_id: backupId });
}
