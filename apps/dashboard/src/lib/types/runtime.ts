/**
 * Type definitions for runtime orchestration, process monitoring, and storage management.
 */

export type ServiceState = 'running' | 'stopped' | 'crashed' | 'starting' | 'stopping';

export interface ProcessInfo {
  name: string;
  command: string[];
  cwd: string;
  port?: number | null;
  health_endpoint?: string | null;
  auto_restart: boolean;
  pid?: number | null;
  state: ServiceState;
  restart_count: number;
  started_at?: number | null;
  uptime_sec: number;
}

export interface RuntimeStatus {
  supervisor_pid: number;
  uptime_seconds: number;
  services: Record<string, ProcessInfo>;
  queue: Record<string, number>;
  storage: Record<string, any>;
  system: {
    cpu_count: number;
    memory_used_percent: number;
  };
}

export interface EnvCheckItem {
  name: string;
  passed: boolean;
  message: string;
  details?: Record<string, any> | null;
}

export interface EnvCheckReport {
  all_passed: boolean;
  base_dir: string;
  python_path: string;
  virtual_env_active: boolean;
  checks: EnvCheckItem[];
}

export interface WorkerJob {
  job_id: string;
  task_type: string;
  payload: Record<string, any>;
  priority: number;
  status: 'queued' | 'running' | 'completed' | 'failed' | 'dead_letter';
  created_at: string;
  started_at?: string | null;
  completed_at?: string | null;
  attempts: number;
  max_attempts: number;
  worker_id?: string | null;
  error_message?: string | null;
  result_data?: Record<string, any> | null;
}

export interface StorageDirectoryStats {
  category: string;
  path: string;
  file_count: number;
  total_bytes: number;
  total_mb: number;
  oldest_timestamp?: number | null;
  newest_timestamp?: number | null;
}

export interface StorageStats {
  categories: Record<string, StorageDirectoryStats>;
  total_files: number;
  total_mb: number;
}

export interface DatabaseBackup {
  backup_id: string;
  database_type: string;
  source_name: string;
  filename: string;
  relative_path: string;
  size_bytes: number;
  sha256: string;
  table_counts: Record<string, number>;
  created_at: string;
  is_compressed: boolean;
  notes?: string | null;
}
