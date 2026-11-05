import React from "react";
import { SearchBar } from "../ui/search-bar";
import { Select } from "../ui/select";

export interface FilterToolbarProps {
  searchQuery?: string;
  search?: string;
  onSearchChange: (q: string) => void;
  bandFilter?: string;
  riskBand?: string;
  onBandFilterChange?: (b: string) => void;
  onRiskBandChange?: (b: string) => void;
  sortBy?: string;
  onSortByChange?: (s: string) => void;
  onExportClick?: () => void;
}

export function FilterToolbar({
  searchQuery,
  search,
  onSearchChange,
  bandFilter,
  riskBand,
  onBandFilterChange,
  onRiskBandChange,
  sortBy = "risk_desc",
  onSortByChange,
  onExportClick,
}: FilterToolbarProps) {
  const currentSearch = searchQuery ?? search ?? "";
  const currentBand = bandFilter ?? riskBand ?? "all";
  const handleBandChange = onBandFilterChange || onRiskBandChange || (() => {});
  return (
    <div className="flex flex-col sm:flex-row items-center gap-3 w-full">
      <div className="w-full sm:flex-1">
        <SearchBar
          placeholder="Search by handle or account ID..."
          value={currentSearch}
          onChange={(e) => onSearchChange(e.target.value)}
          onClear={() => onSearchChange("")}
        />
      </div>

      <div className="flex items-center gap-3 w-full sm:w-auto">
        <div className="w-36">
          <Select
            value={currentBand}
            onChange={(e) => handleBandChange(e.target.value)}
            options={[
              { value: "all", label: "All Risk Bands" },
              { value: "critical", label: "Critical Risk" },
              { value: "high", label: "High Risk" },
              { value: "medium", label: "Medium Risk" },
              { value: "low", label: "Low Risk" },
              { value: "insufficient_evidence", label: "Insufficient Evidence" },
            ]}
          />
        </div>

        <div className="w-36">
          <Select
            value={sortBy}
            onChange={(e) => (onSortByChange ? onSortByChange(e.target.value) : undefined)}
            options={[
              { value: "score_desc", label: "Score: High to Low" },
              { value: "score_asc", label: "Score: Low to High" },
              { value: "username_asc", label: "Handle: A to Z" },
            ]}
          />
        </div>
      </div>
    </div>
  );
}
