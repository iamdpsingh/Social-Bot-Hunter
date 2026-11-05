"use client";

import React from "react";
import { AlertCircle, RotateCcw } from "lucide-react";
import { Button } from "../../../../../components/ui/button";

export default function AccountDetailError({
  error,
  reset,
}: {
  error: Error & { digest?: string };
  reset: () => void;
}) {
  return (
    <div
      className="flex flex-col items-center justify-center p-8 text-center rounded-lg border border-border bg-card space-y-4 my-8"
      data-testid="account-detail-error"
    >
      <div className="p-3 rounded-full bg-rose-500/10 text-rose-500">
        <AlertCircle className="h-8 w-8" />
      </div>
      <div className="space-y-1">
        <h3 className="text-base font-semibold text-foreground">Unable to load account assessment</h3>
        <p className="text-xs text-muted-foreground max-w-sm">
          {error.message || "Account record or evidence could not be retrieved."}
        </p>
      </div>
      <Button onClick={reset} className="gap-2">
        <RotateCcw className="h-3.5 w-3.5" />
        Retry Assessment
      </Button>
    </div>
  );
}
