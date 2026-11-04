"use client";

import React, { useState } from "react";
import { Header } from "./header";
import { Sidebar } from "./sidebar";
import { LaunchScanModal } from "../overview/launch-scan-modal";

export interface AppShellProps {
  children: React.ReactNode;
}

export function AppShell({ children }: AppShellProps) {
  const [isLaunchModalOpen, setIsLaunchModalOpen] = useState(false);

  return (
    <div className="min-h-screen bg-background text-foreground flex flex-col">
      <Header onNewScanClick={() => setIsLaunchModalOpen(true)} />
      <div className="flex flex-1">
        <Sidebar />
        <main className="flex-1 overflow-y-auto p-6 lg:p-8 max-w-7xl mx-auto w-full">
          {children}
        </main>
      </div>

      <LaunchScanModal
        isOpen={isLaunchModalOpen}
        onClose={() => setIsLaunchModalOpen(false)}
      />
    </div>
  );
}
