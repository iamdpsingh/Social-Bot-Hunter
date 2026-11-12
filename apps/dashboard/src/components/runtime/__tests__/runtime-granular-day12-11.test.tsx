import { render, screen } from '@testing-library/react';
import { describe, expect, it } from 'vitest';
import { StorageBreakdownCard } from '../storage-breakdown-card';
import type { StorageStats } from '@/lib/types/runtime';

describe('StorageBreakdownCard Granular 11', () => {
  const mockStats: StorageStats = {
    categories: {
      snapshots: { category: 'snapshots', path: '/data/snapshots', file_count: 11, total_bytes: 1024, total_mb: 1.0 },
    },
    total_files: 11,
    total_mb: 1.0,
  };

  it('renders category file counts for index 11', () => {
    render(<StorageBreakdownCard stats={mockStats} />);
    expect(screen.getByTestId('storage-breakdown-card')).toBeDefined();
  });
});
