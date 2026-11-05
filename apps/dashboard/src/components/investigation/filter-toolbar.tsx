import React from "react";
import { SearchBar } from "../ui/search-bar";
import { Select } from "../ui/select";

export interface FilterToolbarProps {
  searchQuery: string;
  onSearchChange: (q: string) => void;
  bandFilter: string;
  onBandFilterChange: (b: string) => void;
  sortBy: string;
  onSortByChange: (s: string) => void;
}

export function FilterToolbar({
  searchQuery,
  onSearchChange,
  bandFilter,
  onBandFilterChange,
  sortBy,
  onSortByChange,
}: FilterToolbarProps) {
  return (
    <div className="flex flex-col sm:flex-row items-center gap-3 w-full">
      <div className="w-full sm:flex-1">
        <SearchBar
          placeholder="Search by handle or account ID..."
          value={searchQuery}
          onChange={(e) => onSearchChange(e.target.value)}
          onClear={() => onSearchChange("")}
        />
      </div>

      <div className="flex items-center gap-3 w-full sm:w-auto">
        <div className="w-36">
          <Select
            value={bandFilter}
            onChange={(e) => onBandFilterChange(e.target.value)}
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
            onChange={(e) => onSortByChange(e.target.value)}
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
