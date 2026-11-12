import { render, screen } from '@testing-library/react';
import { describe, expect, it } from 'vitest';
import { ProcessSupervisorCard } from '../process-supervisor-card';
import type { RuntimeStatus } from '@/lib/types/runtime';

describe('ProcessSupervisorCard', () => {
  const mockStatus: RuntimeStatus = {
    supervisor_pid: 12345,
    uptime_seconds: 420,
    services: {
      api: {
        name: 'api',
        command: ['python', '-m', 'uvicorn'],
        cwd: '.',
        port: 8000,
        state: 'running',
        pid: 12346,
        restart_count: 0,
        uptime_sec: 420,
        auto_restart: true,
      },
    },
    queue: { queued: 1, running: 0, completed: 5 },
    storage: {},
    system: { cpu_count: 8, memory_used_percent: 45.2 },
  };

  it('renders supervisor details and service status badge', () => {
    render(<ProcessSupervisorCard status={mockStatus} />);
    expect(screen.getByText('Local Multi-Service Supervisor')).toBeDefined();
    expect(screen.getByText('RUNNING')).toBeDefined();
    expect(screen.getByText('8 cores')).toBeDefined();
  });
});
