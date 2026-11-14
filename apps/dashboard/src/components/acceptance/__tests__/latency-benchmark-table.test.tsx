import { render, screen } from '@testing-library/react';
import React from 'react';
import { describe, expect, it } from 'vitest';
import { LatencyBenchmarkTable } from '../latency-benchmark-table';

describe('LatencyBenchmarkTable', () => {
  it('renders benchmark tasks and pass status', () => {
    render(
      <LatencyBenchmarkTable
        entries={[
          {
            taskName: 'sqlite_in_memory_query',
            p50Ms: 0.001,
            p90Ms: 0.001,
            p99Ms: 0.002,
            slaLimitMs: 5.0,
            passedSla: true,
            throughputOpsSec: 1000000,
          },
        ]}
      />
    );
    expect(screen.getByText('Latency Benchmarks & SLAs')).toBeInTheDocument();
    expect(screen.getByText('sqlite_in_memory_query')).toBeInTheDocument();
    expect(screen.getByText('PASS')).toBeInTheDocument();
  });
});
