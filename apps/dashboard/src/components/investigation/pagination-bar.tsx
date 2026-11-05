import React from "react";
import { ChevronLeft, ChevronRight } from "lucide-react";
import { Button } from "../ui/button";

export interface PaginationBarProps {
  total?: number;
  limit?: number;
  offset?: number;
  currentPage?: number;
  totalPages?: number;
  onPageChange: (newPageOrOffset: number) => void;
  onLimitChange?: (newLimit: number) => void;
}

export function PaginationBar({
  total: propTotal,
  limit: propLimit = 25,
  offset: propOffset,
  currentPage: propCurrentPage,
  totalPages: propTotalPages,
  onPageChange,
  onLimitChange,
}: PaginationBarProps) {
  const total = propTotal ?? (propTotalPages ? propTotalPages * propLimit : 0);
  const limit = propLimit;
  const offset = propOffset ?? (propCurrentPage ? (propCurrentPage - 1) * limit : 0);
  const currentPage = propCurrentPage ?? Math.floor(offset / limit) + 1;
  const totalPages = propTotalPages ?? Math.max(1, Math.ceil(total / limit));
  const hasPrev = offset > 0 || (propCurrentPage !== undefined && propCurrentPage > 1);
  const hasNext = offset + limit < total || (propCurrentPage !== undefined && propCurrentPage < totalPages);

  return (
    <div className="flex flex-col sm:flex-row items-center justify-between gap-4 py-3 text-xs text-muted-foreground">
      <div>
        Showing <span className="font-semibold text-foreground">{Math.min(offset + 1, total)}</span> to{" "}
        <span className="font-semibold text-foreground">{Math.min(offset + limit, total)}</span> of{" "}
        <span className="font-semibold text-foreground">{total}</span> accounts
      </div>

      <div className="flex items-center gap-2">
        {onLimitChange && (
          <select
            value={limit}
            onChange={(e) => onLimitChange(Number(e.target.value))}
            className="h-8 rounded border border-white/10 bg-slate-900 px-2 text-xs text-foreground"
          >
            <option value="10">10 per page</option>
            <option value="25">25 per page</option>
            <option value="50">50 per page</option>
            <option value="100">100 per page</option>
          </select>
        )}

        <Button
          size="sm"
          variant="outline"
          disabled={!hasPrev}
          onClick={() => onPageChange(Math.max(0, offset - limit))}
          className="h-8 w-8 p-0"
          aria-label="Previous page"
        >
          <ChevronLeft className="h-4 w-4" />
        </Button>
        <span className="font-mono text-xs text-foreground px-2">
          {currentPage} / {totalPages}
        </span>
        <Button
          size="sm"
          variant="outline"
          disabled={!hasNext}
          onClick={() => onPageChange(offset + limit)}
          className="h-8 w-8 p-0"
          aria-label="Next page"
        >
          <ChevronRight className="h-4 w-4" />
        </Button>
      </div>
    </div>
  );
}
