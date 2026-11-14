import { render, screen } from '@testing-library/react';
import React from 'react';
import { describe, expect, it } from 'vitest';
import { LaunchChecklistCard } from '../launch-checklist-card';

describe('LaunchChecklistCard', () => {
  it('renders milestone days and commit tags', () => {
    render(
      <LaunchChecklistCard
        items={[
          {
            dayNumber: 1,
            title: 'Foundations & Architecture',
            status: 'COMPLETED',
            commitsCount: 154,
            signoffDate: '2026-11-01',
          },
        ]}
      />
    );
    expect(screen.getByText('14-Day Delivery Checklist')).toBeInTheDocument();
    expect(screen.getByText('Day 1: Foundations & Architecture')).toBeInTheDocument();
    expect(screen.getByText('154+ commits')).toBeInTheDocument();
  });
});
