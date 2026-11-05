import React from "react";
import { FilterX } from "lucide-react";
import { Button } from "../ui/button";

export interface EmptyAccountsStateProps {
  onResetFilters?: () => void;
}

export function EmptyAccountsState({ onResetFilters }: EmptyAccountsStateProps) {
  return (
    <div className="flex flex-col items-center justify-center p-12 text-center border border-dashed border-white/10 rounded-lg bg-slate-900/30">
      <FilterX className="h-8 w-8 text-muted-foreground mb-3" />
      <h3 className="text-sm font-semibold text-foreground">No accounts match query</h3>
      <p className="text-xs text-muted-foreground mt-1 max-w-sm">
        Try adjusting your search criteria, clearing the risk band filter, or verifying scan completeness.
      </p>
      {onResetFilters && (
        <Button size="sm" variant="outline" onClick={onResetFilters} className="mt-4">
          Reset Search Filters
        </Button>
      )}
    </div>
  );
}
