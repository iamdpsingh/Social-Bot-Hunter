"use client";

import React from "react";
import Link from "next/link";
import { usePathname } from "next/navigation";
import {
  LayoutDashboard,
  Users,
  Network,
  Share2,
  History,
  Settings,
  HelpCircle,
  FileCode,
} from "lucide-react";
import { cn } from "../../lib/utils";

export const NAVIGATION_ITEMS = [
  { name: "Overview", href: "/", icon: LayoutDashboard },
  { name: "Investigations", href: "/investigations", icon: Users },
  { name: "Network Explorer", href: "/network", icon: Network },
  { name: "Coordinated Activity", href: "/coordination", icon: Share2 },
  { name: "Scan History & Diff", href: "/history", icon: History },
  { name: "Settings & Capabilities", href: "/settings", icon: Settings },
];

export function Sidebar() {
  const pathname = usePathname();

  return (
    <aside className="hidden lg:flex w-64 flex-col border-r border-white/5 bg-card/40 backdrop-blur-md justify-between min-h-[calc(100vh-4rem)]">
      <div className="p-4 space-y-6">
        <div className="space-y-1">
          <p className="px-3 text-[11px] font-semibold uppercase tracking-wider text-muted-foreground/70">
            Workspace
          </p>
          <nav className="space-y-1 pt-1" aria-label="Main Navigation">
            {NAVIGATION_ITEMS.map((item) => {
              const isActive = pathname === item.href || (item.href !== "/" && pathname?.startsWith(item.href));
              const Icon = item.icon;

              return (
                <Link
                  key={item.name}
                  href={item.href}
                  className={cn(
                    "flex items-center gap-3 rounded-lg px-3 py-2 text-xs font-medium transition-colors",
                    isActive
                      ? "bg-primary/10 text-primary font-semibold border border-primary/20"
                      : "text-muted-foreground hover:bg-white/5 hover:text-foreground"
                  )}
                >
                  <Icon className={cn("h-4 w-4", isActive ? "text-primary" : "text-muted-foreground")} />
                  {item.name}
                </Link>
              );
            })}
          </nav>
        </div>

        <div className="space-y-1">
          <p className="px-3 text-[11px] font-semibold uppercase tracking-wider text-muted-foreground/70">
            Documentation
          </p>
          <nav className="space-y-1 pt-1" aria-label="Documentation Navigation">
            <a
              href="http://localhost:8080/docs"
              target="_blank"
              rel="noreferrer"
              className="flex items-center gap-3 rounded-lg px-3 py-2 text-xs font-medium text-muted-foreground hover:bg-white/5 hover:text-foreground transition-colors"
            >
              <FileCode className="h-4 w-4 text-muted-foreground" />
              OpenAPI Specification
            </a>
            <a
              href="https://github.com/iamdpsingh/Social-Bot-Hunter"
              target="_blank"
              rel="noreferrer"
              className="flex items-center gap-3 rounded-lg px-3 py-2 text-xs font-medium text-muted-foreground hover:bg-white/5 hover:text-foreground transition-colors"
            >
              <HelpCircle className="h-4 w-4 text-muted-foreground" />
              Architecture Docs
            </a>
          </nav>
        </div>
      </div>

      <div className="p-4 border-t border-white/5 text-[11px] text-muted-foreground/70 space-y-1">
        <p className="font-semibold text-foreground">Provenance & Safety</p>
        <p>Evidence-backed risk scores. Never claims absolute certainty without ground truth.</p>
      </div>
    </aside>
  );
}
