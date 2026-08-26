"use client";

import { useEffect, useMemo, useState } from "react";
import Link from "next/link";
import { DatasetBanner, PageHeader } from "@/components/layout/shell";
import { Badge, Card } from "@/components/ui/primitives";
import { api, type Banner } from "@/lib/api";

type Opp = {
  opportunity_id: string;
  rank: number;
  title: string;
  frequency: number;
  purchase_association: number;
  evidence_strength: number;
  confidence: string;
  research_gap: string;
  composite_score: number;
  user_segment: string[];
  existing_workaround: string[];
};

export default function OpportunitiesPage() {
  const [rows, setRows] = useState<Opp[]>([]);
  const [banner, setBanner] = useState<Banner>();
  const [sort, setSort] = useState("rank");
  const [q, setQ] = useState("");

  useEffect(() => {
    api<Opp[]>(`/api/opportunities?sort=${sort}`).then(setRows).catch(() => setRows([]));
    api<Banner>("/api/banner").then(setBanner).catch(() => undefined);
  }, [sort]);

  const filtered = useMemo(
    () => rows.filter((r) => r.title.toLowerCase().includes(q.toLowerCase())),
    [rows, q],
  );

  return (
    <div>
      <DatasetBanner banner={banner} />
      <PageHeader
        title="Opportunity Landscape"
        description="Ranked opportunity areas — not feature ideas. Ranking uses a documented weighted formula. Purchase association means co-occurrence with postponement / abandonment / alternative / still-considering language, not causation."
      />
      <div className="mb-4 flex flex-wrap gap-2">
        <input value={q} onChange={(e) => setQ(e.target.value)} placeholder="Filter by text" className="rounded-md border border-zinc-300 bg-white px-3 py-2 text-sm" />
        <select value={sort} onChange={(e) => setSort(e.target.value)} className="rounded-md border border-zinc-300 bg-white px-3 py-2 text-sm">
          <option value="rank">Rank</option>
          <option value="-frequency">Frequency</option>
          <option value="-purchase_association">Purchase association</option>
          <option value="-evidence_strength">Evidence strength</option>
          <option value="-composite_score">Composite score</option>
        </select>
        <a className="rounded-md border border-zinc-300 bg-white px-3 py-2 text-sm" href="/api/export/opportunities.csv">
          Export CSV
        </a>
      </div>
      <Card className="overflow-x-auto">
        <table className="min-w-full text-left text-sm">
          <thead className="border-b bg-zinc-50 text-xs uppercase text-zinc-500">
            <tr>
              <th className="px-3 py-2">Rank</th>
              <th className="px-3 py-2">Opportunity</th>
              <th className="px-3 py-2">Frequency</th>
              <th className="px-3 py-2">Purchase assoc.</th>
              <th className="px-3 py-2">Evidence</th>
              <th className="px-3 py-2">Confidence</th>
              <th className="px-3 py-2">Research gap</th>
            </tr>
          </thead>
          <tbody>
            {filtered.map((row) => (
              <tr key={row.opportunity_id} className="border-b last:border-0 hover:bg-rose-50/40">
                <td className="px-3 py-3 tabular-nums">{row.rank}</td>
                <td className="px-3 py-3">
                  <Link className="font-medium text-rose-900 hover:underline" href={`/opportunities/${row.opportunity_id}`}>
                    {row.title}
                  </Link>
                </td>
                <td className="px-3 py-3 tabular-nums">{row.frequency}</td>
                <td className="px-3 py-3 tabular-nums">{row.purchase_association}</td>
                <td className="px-3 py-3 tabular-nums">{row.evidence_strength}</td>
                <td className="px-3 py-3"><Badge tone="amber">{row.confidence}</Badge></td>
                <td className="max-w-xs px-3 py-3 text-xs text-zinc-600">{row.research_gap}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </Card>
    </div>
  );
}
