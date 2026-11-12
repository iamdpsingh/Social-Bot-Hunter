import { render, screen } from '@testing-library/react';
import { describe, expect, it } from 'vitest';
import { WorkerQueueCard } from '../worker-queue-card';
import type { WorkerJob } from '@/lib/types/runtime';

describe('WorkerQueueCard', () => {
  const mockJobs: WorkerJob[] = [
    {
      job_id: 'job_123',
      task_type: 'storage.prune',
      payload: {},
      priority: 10,
      status: 'completed',
      created_at: new Date().toISOString(),
      attempts: 1,
      max_attempts: 3,
    },
  ];

  it('renders worker stats and task row', () => {
    render(<WorkerQueueCard jobs={mockJobs} queueStats={{ queued: 2, completed: 10 }} />);
    expect(screen.getByText('Local Background Worker Queue')).toBeDefined();
    expect(screen.getByText('storage.prune')).toBeDefined();
    expect(screen.getByText('Done')).toBeDefined();
  });
});
