"use client";

import React from "react";
import { Users, AlertTriangle, Network, Download, Activity, Share2 } from "lucide-react";
import { cn } from "../../lib/utils";

export type TabType = "overview" | "explorer" | "network" | "features" | "coordination" | "export";

export interface InvestigationTabsProps {
  activeTab: TabType;
  onTabChange: (tab: TabType) => void;
  tabCounts?: Record<string, number>;
}

export function InvestigationTabs({ activeTab, onTabChange, tabCounts }: InvestigationTabsProps) {
  const tabs = [
    { id: "overview" as TabType, label: "Overview & Evidence", icon: AlertTriangle },
    { id: "explorer" as TabType, label: "Followers & Following Explorer", icon: Users },
    { id: "network" as TabType, label: "Interactive Network Explorer", icon: Network },
    { id: "features" as TabType, label: "Risk Features & Metrics", icon: Activity },
    { id: "coordination" as TabType, label: "Coordinated Activity", icon: Share2 },
    { id: "export" as TabType, label: "Export & Provenance", icon: Download },
  ];

  return (
    <div
      role="tablist"
      aria-label="Investigation Workspace Views"
      className="flex items-center gap-1 border-b border-white/5 overflow-x-auto"
    >
      {tabs.map((tab) => {
        const Icon = tab.icon;
        const isActive = activeTab === tab.id;
        const count = tabCounts?.[tab.id];

        return (
          <button
            key={tab.id}
            role="tab"
            id={`tab-${tab.id}`}
            aria-controls={`panel-${tab.id}`}
            aria-selected={isActive}
            tabIndex={isActive ? 0 : -1}
            type="button"
            onClick={() => onTabChange(tab.id)}
            className={cn(
              "flex items-center gap-2 px-4 py-2.5 text-xs font-medium border-b-2 transition-colors whitespace-nowrap",
              isActive
                ? "border-primary text-primary font-semibold"
                : "border-transparent text-muted-foreground hover:text-foreground hover:border-white/10"
            )}
          >
            <Icon className="w-3.5 h-3.5" />
            <span>{tab.label}</span>
            {count !== undefined && (
              <span
                className={cn(
                  "ml-1.5 px-1.5 py-0.5 rounded-full text-[10px]",
                  isActive ? "bg-primary/20 text-primary" : "bg-white/5 text-muted-foreground"
                )}
              >
                {count.toLocaleString()}
              </span>
            )}
          </button>
        );
      })}
    </div>
  );
}
