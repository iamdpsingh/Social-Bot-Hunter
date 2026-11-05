"use client";

import React from "react";
import Link from "next/link";
import { useParams } from "next/navigation";
import { ArrowLeft, Shield, AlertTriangle } from "lucide-react";
import { Button } from "../../../../../components/ui/button";
import { AccountProfileCard } from "../../../../../components/investigation/account-profile-card";
import { RiskGauge } from "../../../../../components/investigation/risk-gauge";
import { FollowerRatioGauge } from "../../../../../components/investigation/follower-ratio-gauge";
import { ContributingSignalBar } from "../../../../../components/investigation/contributing-signal-bar";
import { EvidenceInspector } from "../../../../../components/investigation/evidence-inspector";
import { LimitationsCard } from "../../../../../components/investigation/limitations-card";
import { TimelineSnapshot } from "../../../../../components/investigation/timeline-snapshot";
import { AccountNeighborhoodViewer } from "../../../../../components/investigation/account-neighborhood-viewer";
import { SignalRadarPreview } from "../../../../../components/investigation/signal-radar-preview";
import { SyntheticDataBanner } from "../../../../../components/ui/synthetic-banner";
import { useAccountDetail } from "../../../../../lib/hooks/use-account-detail";
import { useAccountEvidence } from "../../../../../lib/hooks/use-account-evidence";
import { useAccountNeighborhood } from "../../../../../lib/hooks/use-account-neighborhood";

export default function AccountDetailPage() {
  const params = useParams();
  const scanId = typeof params?.id === "string" ? params.id : "";
  const accountId = typeof params?.accountId === "string" ? params.accountId : "";

  const { account, isLoading: isAccLoading } = useAccountDetail(scanId, accountId);
  const { evidence, isLoading: isEvLoading } = useAccountEvidence(scanId, accountId);
  const { neighborhood } = useAccountNeighborhood(scanId, accountId);

  const riskScore = account?.assessment?.risk_score ?? 0.82;
  const confidence = account?.assessment?.confidence ?? 0.91;

  return (
    <div className="space-y-6 pb-12" data-testid="account-detail-page">
      <SyntheticDataBanner />

      <div className="flex items-center justify-between">
        <Link href={`/investigations/${scanId}`}>
          <Button variant="outline" size="sm" className="gap-2 text-xs">
            <ArrowLeft className="h-3.5 w-3.5" />
            Back to Investigation Workspace
          </Button>
        </Link>
        <span className="text-xs font-mono text-muted-foreground">ID: {accountId}</span>
      </div>

      <AccountProfileCard
        username={account?.account?.username || accountId}
        platform={account?.account?.platform || "twitter"}
        riskScore={riskScore}
        confidence={confidence}
        followers={account?.observation?.followers_count ?? 1240}
        following={account?.observation?.following_count ?? 14500}
        postsCount={account?.observation?.posts_count ?? 32}
        observation={account?.observation}
      />

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div className="rounded-lg border border-border bg-card p-5 flex flex-col items-center justify-center text-center space-y-2">
          <h4 className="text-xs font-semibold uppercase tracking-wider text-muted-foreground">
            Overall Risk Evaluation
          </h4>
          <RiskGauge score={riskScore} confidence={confidence} size={150} />
        </div>

        <FollowerRatioGauge
          followers={account?.observation?.followers_count ?? 1240}
          following={account?.observation?.following_count ?? 14500}
        />

        <SignalRadarPreview
          timingScore={0.88}
          textRepetitionScore={0.76}
          networkAnomalyScore={0.62}
          profileScore={0.45}
        />
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-2 space-y-6">
          <div className="rounded-lg border border-border bg-card p-5 space-y-4">
            <h3 className="text-sm font-semibold text-foreground flex items-center gap-2">
              <Shield className="h-4 w-4 text-primary" />
              Contributing Heuristic Signals
            </h3>
            <div className="space-y-3">
              <ContributingSignalBar
                name="High Following-to-Follower Ratio"
                score={0.92}
                weight={0.35}
                contribution={0.32}
              />
              <ContributingSignalBar
                name="Temporal Synchrony with Bot Farm"
                score={0.85}
                weight={0.4}
                contribution={0.34}
              />
              <ContributingSignalBar
                name="Copypasta Linguistic Match"
                score={0.78}
                weight={0.25}
                contribution={0.19}
              />
            </div>
          </div>

          <EvidenceInspector evidence={evidence || []} />
        </div>

        <div className="space-y-6">
          <LimitationsCard
            limitations={[
              "Direct messages and private interactions unobservable under public API tier.",
              "Historical profile photo changes truncated prior to observation window.",
            ]}
          />

          <TimelineSnapshot
            observations={
              account?.observation
                ? [account.observation]
                : [
                    {
                      observed_at: "2026-11-05T08:30:00Z",
                      followers_count: 1240,
                      following_count: 14500,
                      posts_count: 32,
                    },
                  ]
            }
          />

          {neighborhood && (
            <AccountNeighborhoodViewer
              currentAccountId={accountId}
              neighborhood={neighborhood}
            />
          )}
        </div>
      </div>
    </div>
  );
}
