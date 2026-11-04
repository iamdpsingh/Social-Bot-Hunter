import React from "react";
import type { Metadata } from "next";
import "../styles/globals.css";
import { AppShell } from "../components/layout/app-shell";

export const metadata: Metadata = {
  title: "Social Bot Hunter — Analytics & Investigation Platform",
  description: "Cross-platform social media account analysis, bot-risk assessment, and coordinated-network detection platform.",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en" className="dark">
      <body className="bg-background text-foreground antialiased min-h-screen">
        <AppShell>{children}</AppShell>
      </body>
    </html>
  );
}
