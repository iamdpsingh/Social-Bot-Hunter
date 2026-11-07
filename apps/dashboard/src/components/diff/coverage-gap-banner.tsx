"use client";

import React from "react";
import { AlertCircle } from "lucide-react";

interface CoverageGapBannerProps {
  coverageGapsCount: number;
}

export function CoverageGapBanner({ coverageGapsCount }: CoverageGapBannerProps) {
  return (
    <div
      data-testid="coverage-gap-banner"
      className="p-4 rounded-xl border border-amber-500/30 bg-amber-500/10 text-amber-500 flex items-start gap-3 shadow-sm"
    >
      <AlertCircle className="w-5 h-5 flex-shrink-0 mt-0.5" />
      <div className="text-xs leading-relaxed">
        <strong className="font-semibold block text-amber-400 mb-0.5">
          Coverage Gap Transparency ({coverageGapsCount} unobserved accounts)
        </strong>
        Social Bot Hunter strictly distinguishes between <em>proven removals</em> (accounts crawled and verified gone)
        and <em>unobserved gaps</em> (accounts that were merely omitted from subsequent scan samples due to rate limits or crawl depth).
        Never mistake incomplete crawl coverage for genuine network disruption.
      </div>
    </div>
  );
}
