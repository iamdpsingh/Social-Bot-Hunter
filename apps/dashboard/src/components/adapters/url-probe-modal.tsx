"use client";

import React, { useState } from "react";
import { Search, Loader2, CheckCircle2, AlertTriangle, ExternalLink, Users, Video } from "lucide-react";
import { Modal } from "../ui/modal";
import { Button } from "../ui/button";
import { Badge } from "../ui/badge";
import { useUrlProbe } from "../../lib/hooks/use-url-probe";

interface UrlProbeModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSelectTarget?: (platform: string, targetId: string) => void;
}

export function UrlProbeModal({ isOpen, onClose, onSelectTarget }: UrlProbeModalProps) {
  const [inputUrl, setInputUrl] = useState("");
  const { state, urlInfo, probeResult, errorMessage, probe, reset } = useUrlProbe();

  const handleProbe = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!inputUrl.trim()) return;
    await probe(inputUrl.trim());
  };

  const handleLaunchScan = () => {
    if (probeResult && probeResult.outcome === "ok" && onSelectTarget) {
      onSelectTarget(probeResult.platform, probeResult.handle);
      handleClose();
    }
  };

  const handleClose = () => {
    reset();
    setInputUrl("");
    onClose();
  };

  return (
    <Modal isOpen={isOpen} onClose={handleClose} title="Profile URL Preflight Probe">
      <form onSubmit={handleProbe} className="space-y-4">
        <div>
          <label htmlFor="probe-url-input" className="block text-xs font-medium text-muted-foreground mb-1">
            Target Account Profile URL or Handle
          </label>
          <div className="relative">
            <input
              id="probe-url-input"
              type="text"
              placeholder="e.g. https://www.youtube.com/@veritasium or https://x.com/elonmusk"
              value={inputUrl}
              onChange={(e) => setInputUrl(e.target.value)}
              disabled={state === "validating" || state === "probing"}
              className="w-full rounded-lg border border-white/10 bg-white/5 px-3 py-2 text-xs text-foreground placeholder:text-muted-foreground/60 focus:border-primary/50 focus:outline-none focus:ring-1 focus:ring-primary/50"
            />
            <Button
              type="submit"
              size="sm"
              disabled={!inputUrl.trim() || state === "validating" || state === "probing"}
              className="absolute right-1 top-1 h-7 text-xs"
            >
              {state === "validating" || state === "probing" ? (
                <>
                  <Loader2 className="mr-1.5 h-3.5 w-3.5 animate-spin" />
                  Probing...
                </>
              ) : (
                <>
                  <Search className="mr-1.5 h-3.5 w-3.5" />
                  Probe
                </>
              )}
            </Button>
          </div>
          <p className="text-[11px] text-muted-foreground mt-1">
            Validates format, checks SSRF safety, canonicalizes URL, and retrieves live profile metrics.
          </p>
        </div>

        {errorMessage && (
          <div className="rounded-lg border border-rose-500/20 bg-rose-500/10 p-3 text-xs text-rose-300 flex items-start gap-2">
            <AlertTriangle className="h-4 w-4 shrink-0 text-rose-400 mt-0.5" />
            <div>
              <p className="font-semibold">Probe Failed</p>
              <p className="text-[11px] opacity-90">{errorMessage}</p>
            </div>
          </div>
        )}

        {probeResult && (
          <div className="rounded-xl border border-white/10 bg-white/5 p-4 space-y-3">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2">
                <Badge variant="success" className="capitalize">
                  {probeResult.platform}
                </Badge>
                <span className="font-mono text-xs font-semibold text-foreground">
                  {probeResult.handle}
                </span>
              </div>
              <span className="text-[11px] text-muted-foreground font-mono">
                1 Quota Unit ({probeResult.daily_quota_remaining.toLocaleString()} left)
              </span>
            </div>

            {probeResult.account && (
              <div className="space-y-2 pt-2 border-t border-white/5">
                <div className="flex items-center justify-between">
                  <span className="text-xs font-semibold text-foreground">
                    {probeResult.account.display_name || probeResult.handle}
                  </span>
                  <a
                    href={probeResult.canonical_url}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="text-[11px] text-primary hover:underline flex items-center gap-1"
                  >
                    Canonical Link <ExternalLink className="h-3 w-3" />
                  </a>
                </div>

                <div className="grid grid-cols-2 gap-2 text-xs text-muted-foreground pt-1">
                  <div className="flex items-center gap-1.5">
                    <Users className="h-3.5 w-3.5 text-primary" />
                    <span>{(probeResult.account.follower_count || 0).toLocaleString()} Followers</span>
                  </div>
                  <div className="flex items-center gap-1.5">
                    <Video className="h-3.5 w-3.5 text-primary" />
                    <span>{(probeResult.account.post_count || 0).toLocaleString()} Posts</span>
                  </div>
                </div>
              </div>
            )}

            {probeResult.limitation && (
              <div className="text-[11px] text-amber-400/90 bg-amber-500/10 border border-amber-500/20 p-2 rounded-lg">
                ⚠️ {probeResult.limitation}
              </div>
            )}
          </div>
        )}

        <div className="flex items-center justify-end gap-2 pt-2 border-t border-white/5">
          <Button type="button" variant="ghost" size="sm" onClick={handleClose}>
            Cancel
          </Button>
          {probeResult && probeResult.outcome === "ok" && onSelectTarget && (
            <Button type="button" size="sm" onClick={handleLaunchScan}>
              <CheckCircle2 className="mr-1.5 h-3.5 w-3.5" />
              Use Target for Scan
            </Button>
          )}
        </div>
      </form>
    </Modal>
  );
}
