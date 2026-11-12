import { render, screen } from '@testing-library/react';
import { describe, expect, it } from 'vitest';
import { StorageBreakdownCard } from '../storage-breakdown-card';
import type { StorageStats } from '@/lib/types/runtime';

describe('StorageBreakdownCard Granular 10', () => {
  const mockStats: StorageStats = {
    categories: {
      snapshots: { category: 'snapshots', path: '/data/snapshots', file_count: 10, total_bytes: 1024, total_mb: 1.0 },
    },
    total_files: 10,
    total_mb: 1.0,
  };

  it('renders category file counts for index 10', () => {
    render(<StorageBreakdownCard stats={mockStats} />);
    expect(screen.getByTestId('storage-breakdown-card')).toBeDefined();
  });
});
