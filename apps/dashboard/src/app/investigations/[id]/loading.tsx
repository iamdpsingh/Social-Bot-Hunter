import React from "react";
import { Skeleton } from "../../../components/ui/skeleton";

export default function InvestigationDetailLoading() {
  return (
    <div className="space-y-6" data-testid="investigation-detail-loading">
      <div className="flex justify-between items-center">
        <Skeleton className="h-10 w-64" />
        <Skeleton className="h-9 w-24" />
      </div>
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
        {[...Array(4)].map((_, i) => (
          <Skeleton key={i} className="h-24 w-full" />
        ))}
      </div>
      <Skeleton className="h-12 w-full" />
      <Skeleton className="h-96 w-full rounded-lg" />
    </div>
  );
}
