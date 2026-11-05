"use client";

import React, { useState } from "react";
import { useParams } from "next/navigation";
import { InvestigationHeader } from "../../../components/investigation/investigation-header";
import { InvestigationTabs, type TabType } from "../../../components/investigation/investigation-tabs";
import { OverviewSummaryCard } from "../../../components/investigation/overview-summary-card";
import { RelationshipTable } from "../../../components/investigation/relationship-table";
import { FilterToolbar } from "../../../components/investigation/filter-toolbar";
import { PaginationBar } from "../../../components/investigation/pagination-bar";
import { ExportDialog } from "../../../components/investigation/export-dialog";
import { ExportPanel } from "../../../components/investigation/export-panel";
import { AccountFeaturesTable } from "../../../components/investigation/account-features-table";
import { EmptyAccountsState } from "../../../components/investigation/empty-accounts-state";
import { SyntheticDataBanner } from "../../../components/ui/synthetic-banner";
import { useInvestigation } from "../../../lib/hooks/use-investigation";
import { useRelationships } from "../../../lib/hooks/use-relationships";
import { useInvestigationExport } from "../../../lib/hooks/use-investigation-export";

export default function InvestigationDetailPage() {
  const params = useParams();
  const scanId = typeof params?.id === "string" ? params.id : "";

  const [activeTab, setActiveTab] = useState<TabType>("overview");
  const [search, setSearch] = useState("");
  const [riskBand, setRiskBand] = useState("all");
  const [sortBy, setSortBy] = useState("risk_desc");
  const [currentPage, setCurrentPage] = useState(1);
  const [isExportModalOpen, setIsExportModalOpen] = useState(false);

  const { scan, report, isLoading: isInvLoading } = useInvestigation(scanId);
  const { relationships, total: totalCount, isLoading: isRelLoading } = useRelationships(scanId);
  const { downloadCsv, downloadJson, isExporting } = useInvestigationExport(scanId);

  const handleExport = async (format: "csv" | "json") => {
    if (format === "csv") {
      await downloadCsv();
    } else {
      await downloadJson();
    }
    setIsExportModalOpen(false);
  };

  const filteredEdges = (relationships || []).filter((edge: any) => {
    const sId = edge.source_account_id || edge.source_id || "";
    const tId = edge.target_account_id || edge.target_id || "";
    const matchSearch =
      sId.toLowerCase().includes(search.toLowerCase()) ||
      tId.toLowerCase().includes(search.toLowerCase());
    return matchSearch;
  });

  return (
    <div className="space-y-6 pb-12" data-testid="investigation-workspace">
      <SyntheticDataBanner />

      <InvestigationHeader
        scanId={scanId}
        target={(scan as any)?.target || scan?.requested_by || "Target Account"}
        platform={scan?.platform || "x"}
        status={scan?.status || "complete"}
        totalAccounts={report?.total_accounts ?? totalCount}
        botAccounts={report?.total_scored ?? 0}
        onExportClick={() => setIsExportModalOpen(true)}
      />

      <InvestigationTabs
        activeTab={activeTab}
        onTabChange={setActiveTab}
      />

      {activeTab === "overview" && (
        <div className="space-y-6">
          <OverviewSummaryCard
            totalAccounts={report?.total_accounts ?? totalCount}
            botAccounts={report?.total_scored ?? 0}
            avgRiskScore={0.64}
            criticalCount={4}
          />

          <div className="rounded-lg border border-border bg-card p-6 space-y-4">
            <h3 className="text-sm font-semibold text-foreground">Primary Relationships Preview</h3>
            <RelationshipTable scanId={scanId} relationships={filteredEdges.slice(0, 10)} />
          </div>
        </div>
      )}

      {activeTab === "explorer" && (
        <div className="space-y-4">
          <FilterToolbar
            search={search}
            onSearchChange={setSearch}
            riskBand={riskBand}
            onRiskBandChange={setRiskBand}
            sortBy={sortBy}
            onSortByChange={setSortBy}
            onExportClick={() => setIsExportModalOpen(true)}
          />

          {filteredEdges.length === 0 ? (
            <EmptyAccountsState onResetFilters={() => { setSearch(""); setRiskBand("all"); }} />
          ) : (
            <>
              <RelationshipTable scanId={scanId} relationships={filteredEdges} />
              <PaginationBar
                currentPage={currentPage}
                totalPages={Math.max(1, Math.ceil(filteredEdges.length / 25))}
                onPageChange={setCurrentPage}
              />
            </>
          )}
        </div>
      )}

      {activeTab === "features" && (
        <div className="space-y-4">
          <AccountFeaturesTable features={(report as any)?.features || []} />
        </div>
      )}

      {activeTab === "export" && (
        <ExportPanel
          scanId={scanId}
          onExportCsv={() => downloadCsv()}
          onExportJson={() => downloadJson()}
          isExporting={isExporting}
        />
      )}

      <ExportDialog
        isOpen={isExportModalOpen}
        onClose={() => setIsExportModalOpen(false)}
        onExport={handleExport}
        isExporting={isExporting}
      />
    </div>
  );
}
