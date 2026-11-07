"use client";

import React from "react";
import Link from "next/link";

interface InvestigationTabsProps {
  scanId: string;
  activeTab: "overview" | "accounts" | "evidence" | "graph" | "coordination";
}

export function InvestigationTabs({ scanId, activeTab }: InvestigationTabsProps) {
  const tabs = [
    { id: "overview", label: "Overview", href: `/investigations/${scanId}` },
    { id: "accounts", label: "Accounts Explorer", href: `/investigations/${scanId}#accounts` },
    { id: "evidence", label: "Evidence Ledger", href: `/investigations/${scanId}#evidence` },
    { id: "graph", label: "Interactive Network Explorer", href: `/investigations/${scanId}/graph` },
    { id: "coordination", label: "Coordinated Activity", href: `/investigations/${scanId}/coordination` },
  ];

  return (
    <nav aria-label="Investigation tabs" className="border-b border-border mb-6">
      <ul className="flex space-x-6">
        {tabs.map((tab) => {
          const isActive = activeTab === tab.id;
          return (
            <li key={tab.id}>
              <Link
                href={tab.href}
                className={`inline-flex items-center pb-3 px-1 border-b-2 text-sm font-medium transition-colors ${
                  isActive
                    ? "border-primary text-primary"
                    : "border-transparent text-muted-foreground hover:text-foreground hover:border-muted-foreground/50"
                }`}
                aria-current={isActive ? "page" : undefined}
              >
                {tab.label}
              </Link>
            </li>
          );
        })}
      </ul>
    </nav>
  );
}
