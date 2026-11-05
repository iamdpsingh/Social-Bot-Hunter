"use client";

import React from "react";
import Link from "next/link";
import { AlertCircle, ArrowLeft, RotateCcw } from "lucide-react";
import { Button } from "../../../components/ui/button";

export default function InvestigationDetailError({
  error,
  reset,
}: {
  error: Error & { digest?: string };
  reset: () => void;
}) {
  return (
    <div
      className="flex flex-col items-center justify-center p-8 text-center rounded-lg border border-border bg-card space-y-4 my-8"
      data-testid="investigation-detail-error"
    >
      <div className="p-3 rounded-full bg-rose-500/10 text-rose-500">
        <AlertCircle className="h-8 w-8" />
      </div>
      <div className="space-y-1">
        <h3 className="text-base font-semibold text-foreground">Failed to load investigation workspace</h3>
        <p className="text-xs text-muted-foreground max-w-sm">
          {error.message || "Investigation record not found or inaccessible."}
        </p>
      </div>
      <div className="flex gap-3">
        <Link href="/investigations">
          <Button variant="outline" className="gap-2">
            <ArrowLeft className="h-3.5 w-3.5" />
            Back to List
          </Button>
        </Link>
        <Button onClick={reset} className="gap-2">
          <RotateCcw className="h-3.5 w-3.5" />
          Retry
        </Button>
      </div>
    </div>
  );
}
