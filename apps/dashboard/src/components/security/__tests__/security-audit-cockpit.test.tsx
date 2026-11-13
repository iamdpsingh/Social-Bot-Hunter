import { render, screen } from '@testing-library/react';
import React from 'react';
import { describe, expect, it } from 'vitest';
import { SecurityAuditCockpit } from '../security-audit-cockpit';

describe('SecurityAuditCockpit', () => {
  it('renders all four security audit panels', () => {
    render(
      <SecurityAuditCockpit
        scorecard={{
          passed_audit: true,
          total_checks: 3,
          passed_checks: 3,
          failed_checks: 0,
          findings: [],
          checks: [],
        }}
        secrets={{ target_dir: '.', total_findings: 0, findings: [], passed: true }}
        privacy={{ passed: true, total_findings: 0, scanned_sources: 5, findings: [] }}
        dependencies={{
          passed: true,
          python: { ecosystem: 'pypi', scanned_packages_count: 10, passed: true, findings: [] },
          node: { ecosystem: 'npm', scanned_packages_count: 5, passed: true, findings: [] },
        }}
      />
    );
    expect(screen.getByText('Security & Compliance Audit')).toBeInTheDocument();
  });
});
