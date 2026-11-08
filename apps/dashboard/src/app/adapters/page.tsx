import React from "react";
import { Metadata } from "next";
import { AdaptersClient } from "./adapters-client";

export const metadata: Metadata = {
  title: "Platform Adapters & Quotas | Social Bot Hunter",
  description: "Manage official YouTube and X platform API adapters, daily quota budgets, and live URL probing.",
};

export default function AdaptersPage() {
  return <AdaptersClient />;
}
