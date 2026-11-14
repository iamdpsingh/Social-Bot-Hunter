import { render, screen } from '@testing-library/react';
import React from 'react';
import { describe, expect, it } from 'vitest';
import { LatencyBenchmarkTable } from '../latency-benchmark-table';

describe('AccGranularDay1407', () => {
  it('renders table headers with empty entries', () => {
    render(<LatencyBenchmarkTable entries={[]} />);
    expect(screen.getByText('Task')).toBeInTheDocument();
    expect(screen.getByText('SLA Limit')).toBeInTheDocument();
  });
});
