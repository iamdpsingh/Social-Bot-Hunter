import { render, screen } from '@testing-library/react';
import React from 'react';
import { describe, expect, it } from 'vitest';
import { LaunchChecklistCard } from '../launch-checklist-card';

describe('AccGranularDay1410', () => {
  it('renders signoff date string correctly', () => {
    render(
      <LaunchChecklistCard
        items={[
          {
            dayNumber: 13,
            title: 'CI/CD & Security Audit',
            status: 'COMPLETED',
            commitsCount: 218,
            signoffDate: '2026-11-13',
          },
        ]}
      />
    );
    expect(screen.getByText('2026-11-13')).toBeInTheDocument();
    expect(screen.getByText('218+ commits')).toBeInTheDocument();
  });
});
