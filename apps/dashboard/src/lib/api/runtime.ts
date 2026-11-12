import type {
  DatabaseBackup,
  EnvCheckReport,
  RuntimeStatus,
  StorageStats,
  WorkerJob,
} from '../types/runtime';

const API_BASE = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

function getHeaders(token?: string): HeadersInit {
  const headers: HeadersInit = { 'Content-Type': 'application/json' };
  if (token) headers['Authorization'] = `Bearer ${token}`;
  return headers;
}

export async function fetchRuntimeStatus(token?: string): Promise<RuntimeStatus> {
  const res = await fetch(`${API_BASE}/api/v1/runtime/status`, { headers: getHeaders(token) });
  if (!res.ok) throw new Error(`Failed to fetch runtime status: ${res.statusText}`);
  return res.json();
}

export async function fetchEnvCheck(noPorts: boolean = false, token?: string): Promise<EnvCheckReport> {
  const res = await fetch(`${API_BASE}/api/v1/runtime/env?no_ports=${noPorts}`, { headers: getHeaders(token) });
  if (!res.ok) throw new Error(`Failed to fetch env check: ${res.statusText}`);
  return res.json();
}

export async function fetchWorkerJobs(status?: string, limit: number = 50, token?: string): Promise<WorkerJob[]> {
  const query = status ? `?status=${status}&limit=${limit}` : `?limit=${limit}`;
  const res = await fetch(`${API_BASE}/api/v1/runtime/worker/jobs${query}`, { headers: getHeaders(token) });
  if (!res.ok) throw new Error(`Failed to fetch worker jobs: ${res.statusText}`);
  return res.json();
}

export async function enqueueWorkerJob(
  taskType: string,
  payload: Record<string, any> = {},
  priority: number = 10,
  token?: string
): Promise<{ job_id: string; status: string }> {
  const res = await fetch(`${API_BASE}/api/v1/runtime/worker/jobs`, {
    method: 'POST',
    headers: getHeaders(token),
    body: JSON.stringify({ task_type: taskType, payload, priority }),
  });
  if (!res.ok) throw new Error(`Failed to enqueue job: ${res.statusText}`);
  return res.json();
}

export async function fetchStorageStats(token?: string): Promise<StorageStats> {
  const res = await fetch(`${API_BASE}/api/v1/storage/stats`, { headers: getHeaders(token) });
  if (!res.ok) throw new Error(`Failed to fetch storage stats: ${res.statusText}`);
  return res.json();
}

export async function triggerStoragePrune(
  options: {
    category?: string;
    maxAgeDays?: number;
    maxSizeMb?: number;
    dryRun?: boolean;
  } = {},
  token?: string
): Promise<any> {
  const res = await fetch(`${API_BASE}/api/v1/storage/prune`, {
    method: 'POST',
    headers: getHeaders(token),
    body: JSON.stringify({
      category: options.category,
      max_age_days: options.maxAgeDays ?? 30,
      max_size_mb: options.maxSizeMb,
      dry_run: options.dryRun ?? false,
    }),
  });
  if (!res.ok) throw new Error(`Failed to prune storage: ${res.statusText}`);
  return res.json();
}

export async function fetchDatabaseBackups(token?: string): Promise<DatabaseBackup[]> {
  const res = await fetch(`${API_BASE}/api/v1/storage/backups`, { headers: getHeaders(token) });
  if (!res.ok) throw new Error(`Failed to fetch backups: ${res.statusText}`);
  const data = await res.json();
  return data.backups;
}

export async function createDatabaseBackup(
  options: {
    compress?: boolean;
    notes?: string;
  } = {},
  token?: string
): Promise<DatabaseBackup> {
  const res = await fetch(`${API_BASE}/api/v1/storage/backups`, {
    method: 'POST',
    headers: getHeaders(token),
    body: JSON.stringify({
      compress: options.compress ?? false,
      notes: options.notes,
    }),
  });
  if (!res.ok) throw new Error(`Failed to create backup: ${res.statusText}`);
  return res.json();
}

export async function verifyDatabaseBackup(
  backupId: string,
  token?: string
): Promise<{
  backup_id: string;
  is_valid: boolean;
  message: string;
}> {
  const res = await fetch(`${API_BASE}/api/v1/storage/backups/verify`, {
    method: 'POST',
    headers: getHeaders(token),
    body: JSON.stringify({ backup_id: backupId }),
  });
  if (!res.ok) throw new Error(`Failed to verify backup: ${res.statusText}`);
  return res.json();
}
