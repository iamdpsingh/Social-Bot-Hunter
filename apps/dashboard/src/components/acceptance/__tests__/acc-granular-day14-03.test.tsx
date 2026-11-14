import { render, screen } from '@testing-library/react';
import React from 'react';
import { describe, expect, it } from 'vitest';
import { LaunchChecklistCard } from '../launch-checklist-card';

describe('AccGranularDay1403', () => {
  it('renders Day 14 milestone entry', () => {
    render(
      <LaunchChecklistCard
        items={[
          {
            dayNumber: 14,
            title: 'Production Acceptance & Handover',
            status: 'COMPLETED',
            commitsCount: 160,
            signoffDate: '2026-11-14',
          },
        ]}
      />
    );
    expect(screen.getByText('Day 14: Production Acceptance & Handover')).toBeInTheDocument();
  });
});
