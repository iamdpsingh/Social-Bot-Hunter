import { render, screen } from '@testing-library/react';
import React from 'react';
import { describe, expect, it } from 'vitest';
import { PrivacyAuditCard } from '../privacy-audit-card';

describe('GranularSecurityDay13_05', () => {
  it('renders privacy card case 05', () => {
    render(
      <PrivacyAuditCard
        privacy={{
          passed: true,
          total_findings: 0,
          scanned_sources: 5,
          findings: [],
        }}
      />
    );
    expect(screen.getByText('5')).toBeInTheDocument();
  });
});
