import React from "react";
import { RefreshCw } from "lucide-react";
import { cn } from "../../lib/utils";

export interface RefreshCountdownProps {
  secondsRemaining: number;
  onRefresh?: () => void;
  isRefreshing?: boolean;
  className?: string;
}

export function RefreshCountdown({
  secondsRemaining,
  onRefresh,
  isRefreshing = false,
  className,
}: RefreshCountdownProps) {
  return (
    <div
      className={cn(
        "inline-flex items-center gap-2 rounded-lg border border-white/5 bg-white/5 px-2.5 py-1 text-xs text-muted-foreground",
        className
      )}
    >
      <span className="text-[11px] font-mono">Auto-refreshes in {secondsRemaining}s</span>
      {onRefresh && (
        <button
          type="button"
          onClick={onRefresh}
          disabled={isRefreshing}
          className="text-muted-foreground hover:text-foreground transition-colors disabled:opacity-50"
          aria-label="Refresh now"
        >
          <RefreshCw className={cn("h-3 w-3", isRefreshing && "animate-spin")} />
        </button>
      )}
    </div>
  );
}
