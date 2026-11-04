"use client";

import React, { useEffect } from "react";
import { AlertCircle, RefreshCw } from "lucide-react";
import { Button } from "../components/ui/button";

export default function ErrorBoundary({
  error,
  reset,
}: {
  error: Error & { digest?: string };
  reset: () => void;
}) {
  useEffect(() => {
    console.error("Dashboard error caught by boundary:", error);
  }, [error]);

  return (
    <div className="flex flex-col items-center justify-center min-h-[50vh] text-center p-6">
      <div className="h-12 w-12 rounded-full bg-red-500/10 text-red-400 flex items-center justify-center mb-4 border border-red-500/20">
        <AlertCircle className="h-6 w-6" />
      </div>
      <h2 className="text-lg font-semibold text-foreground">Something went wrong</h2>
      <p className="text-xs text-muted-foreground mt-1 max-w-md">
        An unexpected error occurred while rendering the investigation dashboard. Details: {error.message}
      </p>
      <Button onClick={() => reset()} className="mt-6 gap-2" size="sm">
        <RefreshCw className="h-4 w-4" /> Try again
      </Button>
    </div>
  );
}
