"use client";

import React, { useState } from "react";
import { Modal } from "../ui/modal";
import { Button } from "../ui/button";
import { Input } from "../ui/input";
import { Select } from "../ui/select";
import { useScans } from "../../lib/hooks/use-scans";
import type { Platform } from "../../lib/api/types";
import { Alert } from "../ui/alert";

export interface LaunchScanModalProps {
  isOpen: boolean;
  onClose: () => void;
}

export function LaunchScanModal({ isOpen, onClose }: LaunchScanModalProps) {
  const { createScan } = useScans();
  const [platform, setPlatform] = useState<Platform>("x");
  const [targetAccount, setTargetAccount] = useState("");
  const [scope, setScope] = useState<"quick" | "deep" | "comprehensive">("quick");
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!targetAccount.trim()) {
      setError("Target account username or profile URL is required");
      return;
    }

    setIsLoading(true);
    setError(null);
    try {
      await createScan({
        platform,
        target_account: targetAccount.trim(),
        scope,
      });
      onClose();
      setTargetAccount("");
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : "Failed to initiate scan");
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <Modal
      isOpen={isOpen}
      onClose={onClose}
      title="Start New Investigation Scan"
      description="Queue an evidence-driven analysis job for suspicious followers and coordinated networks."
    >
      <form onSubmit={handleSubmit} className="space-y-4 pt-2">
        {error && (
          <Alert variant="destructive" title="Error">
            {error}
          </Alert>
        )}

        <Select
          label="Social Media Platform"
          value={platform}
          onChange={(e) => setPlatform(e.target.value as Platform)}
          options={[
            { value: "x", label: "X (Twitter) — API v2" },
            { value: "instagram", label: "Instagram — Graph API" },
            { value: "tiktok", label: "TikTok — Research API" },
            { value: "youtube", label: "YouTube — Data API v3" },
            { value: "linkedin", label: "LinkedIn — Community Management" },
          ]}
        />

        <Input
          label="Target Profile / Handle"
          placeholder="@username or profile URL"
          value={targetAccount}
          onChange={(e) => setTargetAccount(e.target.value)}
          helperText="Identifier or canonical handle to be validated against the capability registry."
        />

        <Select
          label="Investigation Scope"
          value={scope}
          onChange={(e) => setScope(e.target.value as "quick" | "deep" | "comprehensive")}
          options={[
            { value: "quick", label: "Quick Scan (1 hop, 1,000 recent relationships)" },
            { value: "deep", label: "Deep Scan (2 hops, 10,000 relationships, SimHash content)" },
            { value: "comprehensive", label: "Comprehensive (Full available graph + Temporal sync)" },
          ]}
        />

        <div className="flex items-center justify-end gap-3 pt-3 border-t border-white/5">
          <Button type="button" variant="ghost" onClick={onClose} disabled={isLoading}>
            Cancel
          </Button>
          <Button type="submit" isLoading={isLoading}>
            Start Investigation
          </Button>
        </div>
      </form>
    </Modal>
  );
}
