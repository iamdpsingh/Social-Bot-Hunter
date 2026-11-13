import { render, screen } from '@testing-library/react';
import React from 'react';
import { describe, expect, it } from 'vitest';
import { PrivacyAuditCard } from '../privacy-audit-card';

describe('GranularSecurityDay13_13', () => {
  it('renders privacy card case 13', () => {
    render(
      <PrivacyAuditCard
        privacy={{
          passed: true,
          total_findings: 0,
          scanned_sources: 13,
          findings: [],
        }}
      />
    );
    expect(screen.getByText('13')).toBeInTheDocument();
  });
});
