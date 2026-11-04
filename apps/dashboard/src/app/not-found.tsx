import React from "react";
import Link from "next/link";
import { HelpCircle, ArrowLeft } from "lucide-react";

export default function NotFound() {
  return (
    <div className="flex flex-col items-center justify-center min-h-[50vh] text-center p-6">
      <div className="h-12 w-12 rounded-full bg-slate-800 text-slate-400 flex items-center justify-center mb-4 border border-white/5">
        <HelpCircle className="h-6 w-6" />
      </div>
      <h2 className="text-lg font-semibold text-foreground">Page Not Found</h2>
      <p className="text-xs text-muted-foreground mt-1 max-w-md">
        The requested investigation view or route does not exist. Check the URL or return to the overview dashboard.
      </p>
      <Link
        href="/"
        className="mt-6 inline-flex items-center gap-2 h-9 px-4 py-2 rounded-md bg-primary text-primary-foreground text-xs font-medium hover:bg-primary/90 transition-colors"
      >
        <ArrowLeft className="h-4 w-4" /> Return to Overview
      </Link>
    </div>
  );
}
