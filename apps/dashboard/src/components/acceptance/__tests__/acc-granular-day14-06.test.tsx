import { render, screen } from '@testing-library/react';
import React from 'react';
import { describe, expect, it } from 'vitest';
import { LatencyBenchmarkTable } from '../latency-benchmark-table';

describe('AccGranularDay1406', () => {
  it('renders FAIL badge on SLA breach', () => {
    render(
      <LatencyBenchmarkTable
        entries={[
          {
            taskName: 'slow_task',
            p50Ms: 10.0,
            p90Ms: 20.0,
            p99Ms: 100.0,
            slaLimitMs: 5.0,
            passedSla: false,
            throughputOpsSec: 10,
          },
        ]}
      />
    );
    expect(screen.getByText('FAIL')).toBeInTheDocument();
  });
});
