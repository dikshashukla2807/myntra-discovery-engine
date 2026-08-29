"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { DatasetBanner, PageHeader } from "@/components/layout/shell";
import { Badge, Card } from "@/components/ui/primitives";
import { api, type Banner } from "@/lib/api";

type Opp = {
  opportunity_id: string;
  rank: number;
  title: string;
  frequency: number;
  frequency_percentage: number;
  purchase_association: number;
  evidence_strength: number;
  confidence: string;
  research_gap: string;
  origin?: string;
  source_hypothesis?: string | null;
  source_hypothesis_name?: string | null;
};

export default function OpportunitiesPage() {
  const [rows, setRows] = useState<Opp[]>([]);
  const [banner, setBanner] = useState<Banner>();
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    setLoading(true);
    api<Opp[]>("/api/opportunities?sort=rank")
      .then((data) => {
        setRows(data);
        setError(null);
      })
      .catch((err: Error) => {
        setRows([]);
        setError(err.message);
      })
      .finally(() => setLoading(false));
    api<Banner>("/api/banner").then(setBanner).catch(() => undefined);
  }, []);

  return (
    <div>
      <DatasetBanner banner={banner} />
      <PageHeader
        title="Opportunity Landscape"
        description="Candidate areas only — not features to build. Purchase association is how often postponed, abandoned, or alternative-purchase language shows up in the same cluster. That is not causation."
      />
      {error ? (
        <Card className="mb-4 p-5">
          <p className="font-medium">Could not load opportunities.</p>
          <p className="mt-2 text-sm text-zinc-600">{error}</p>
        </Card>
      ) : null}
      {loading ? <p className="mb-4 text-sm text-zinc-500">Loading landscape…</p> : null}
      {!loading && !error && rows.length === 0 ? (
        <Card className="mb-4 p-5">
          <p className="font-medium">No opportunity areas yet.</p>
          <p className="mt-2 text-sm text-zinc-600">Run the pipeline on collected public comments, then refresh.</p>
        </Card>
      ) : null}
      <Card className="overflow-x-auto">
        <table className="min-w-full text-left text-sm">
          <thead className="border-b bg-zinc-50 text-xs uppercase text-zinc-500">
            <tr>
              <th className="px-3 py-2">Rank</th>
              <th className="px-3 py-2">Opportunity</th>
              <th className="px-3 py-2">Frequency</th>
              <th className="px-3 py-2">% Relevant</th>
              <th className="px-3 py-2">Purchase assoc.</th>
              <th className="px-3 py-2">Evidence (1–5)</th>
              <th className="px-3 py-2">Confidence</th>
              <th className="px-3 py-2">Source</th>
              <th className="px-3 py-2">Research gap</th>
            </tr>
          </thead>
          <tbody>
            {rows.map((row) => (
              <tr key={row.opportunity_id} className="border-b last:border-0 hover:bg-rose-50/40">
                <td className="px-3 py-3 tabular-nums">{row.rank}</td>
                <td className="px-3 py-3">
                  <Link className="font-medium text-rose-900 hover:underline" href={`/opportunities/${row.opportunity_id}`}>
                    {row.title}
                  </Link>
                </td>
                <td className="px-3 py-3 tabular-nums">{row.frequency}</td>
                <td className="px-3 py-3 tabular-nums">{row.frequency_percentage}</td>
                <td className="px-3 py-3 tabular-nums">{row.purchase_association}</td>
                <td className="px-3 py-3 tabular-nums">{row.evidence_strength}</td>
                <td className="px-3 py-3"><Badge tone="amber">{row.confidence}</Badge></td>
                <td className="px-3 py-3">
                  {row.origin === "emerging" || !row.source_hypothesis ? (
                    <Badge tone="sky">Emerging opportunity</Badge>
                  ) : (
                    <Badge>{row.source_hypothesis} {row.source_hypothesis_name || ""}</Badge>
                  )}
                </td>
                <td className="max-w-xs px-3 py-3 text-xs text-zinc-600">{row.research_gap}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </Card>
    </div>
  );
}
