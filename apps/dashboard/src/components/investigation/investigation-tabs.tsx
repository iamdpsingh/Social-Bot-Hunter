import React from "react";
import { Users, AlertTriangle, Network, Download } from "lucide-react";
import { cn } from "../../lib/utils";

export type TabType = "overview" | "explorer" | "features" | "export";

export interface InvestigationTabsProps {
  activeTab: TabType;
  onTabChange: (tab: TabType) => void;
}

export function InvestigationTabs({ activeTab, onTabChange }: InvestigationTabsProps) {
  const tabs = [
    { id: "overview" as TabType, label: "Overview & Evidence", icon: AlertTriangle },
    { id: "explorer" as TabType, label: "Followers & Following Explorer", icon: Users },
    { id: "features" as TabType, label: "Risk Features & Graph", icon: Network },
    { id: "export" as TabType, label: "Export & Provenance", icon: Download },
  ];

  return (
    <div className="flex items-center gap-1 border-b border-white/5 overflow-x-auto">
      {tabs.map((tab) => {
        const Icon = tab.icon;
        const isActive = activeTab === tab.id;
        return (
          <button
            key={tab.id}
            type="button"
            onClick={() => onTabChange(tab.id)}
            className={cn(
              "flex items-center gap-2 px-4 py-2.5 text-xs font-medium border-b-2 transition-colors whitespace-nowrap",
              isActive
                ? "border-primary text-primary font-semibold"
                : "border-transparent text-muted-foreground hover:text-foreground hover:border-white/10"
            )}
          >
            <Icon className="h-4 w-4" />
            {tab.label}
          </button>
        );
      })}
    </div>
  );
}
