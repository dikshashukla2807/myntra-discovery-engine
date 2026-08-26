"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { Bar, BarChart, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";
import { DatasetBanner, PageHeader } from "@/components/layout/shell";
import { Badge, Card } from "@/components/ui/primitives";
import { api, type Banner } from "@/lib/api";

type Overview = {
  banner?: Banner;
  funnel?: Record<string, number>;
  top_opportunities?: Array<{
    opportunity_id: string;
    rank: number;
    title: string;
    frequency: number;
    purchase_association: number;
    confidence: string;
    composite_score: number;
  }>;
  behavioral?: {
    purchase_outcomes?: Record<string, number>;
    barriers?: Record<string, number>;
    external_research_pct?: number;
  };
  quality?: {
    total_collected?: number;
    relevant?: number;
    source_distribution?: { collected?: Record<string, number> };
    disclaimer?: string;
  };
};

export default function OverviewPage() {
  const [data, setData] = useState<Overview | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    api<Overview>("/api/overview")
      .then(setData)
      .catch((err: Error) => setError(err.message));
  }, []);

  if (error) {
    return (
      <Card className="p-6">
        <p className="font-medium">The dashboard has no processed dataset yet.</p>
        <p className="mt-2 text-sm text-zinc-600">{error}</p>
        <p className="mt-4 text-sm">
          Run collection + pipeline, or open Pipeline and start Demo Mode.
        </p>
      </Card>
    );
  }
  if (!data?.funnel) {
    return <p className="text-sm text-zinc-500">Loading overview…</p>;
  }

  const funnel = [
    ["Collected", data.funnel.collected],
    ["Valid", data.funnel.valid],
    ["Relevant", data.funnel.relevant],
    ["Purchase-related", data.funnel.purchase_related],
    ["Wishlist-related", data.funnel.wishlist_related],
  ];
  const sourceRows = Object.entries(data.quality?.source_distribution?.collected || {}).map(
    ([name, value]) => ({ name, value }),
  );
  const barrierRows = Object.entries(data.behavioral?.barriers || {})
    .slice(0, 8)
    .map(([name, value]) => ({ name, value }));

  return (
    <div>
      <DatasetBanner banner={data.banner} />
      <PageHeader
        eyebrow="Business metric"
        title="Why don’t wishlisted items convert within 30 days?"
        description="Growth is trying to increase the share of users who purchase at least one wishlisted item within 30 days — without monetary incentives. This overview only reports what public user-generated content actually contains."
      />

      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-5">
        {funnel.map(([label, value]) => (
          <Card key={String(label)} className="p-4">
            <p className="text-xs uppercase tracking-wide text-zinc-500">{label}</p>
            <p className="mt-2 text-3xl font-semibold tabular-nums">{value ?? 0}</p>
          </Card>
        ))}
      </div>

      <div className="mt-8 grid gap-6 lg:grid-cols-2">
        <Card className="p-5">
          <h3 className="text-sm font-semibold">Where did the public observations come from?</h3>
          <p className="mb-4 mt-1 text-xs text-zinc-500">Actual collected counts. Gaps are not filled with synthetic rows.</p>
          <div className="h-56">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={sourceRows}>
                <XAxis dataKey="name" tick={{ fontSize: 11 }} />
                <YAxis tick={{ fontSize: 11 }} />
                <Tooltip />
                <Bar dataKey="value" fill="#9f1239" radius={[4, 4, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </Card>
        <Card className="p-5">
          <h3 className="text-sm font-semibold">Which barriers show up in relevant comments?</h3>
          <p className="mb-4 mt-1 text-xs text-zinc-500">
            Counts of extracted barrier labels. Presence is not causation of 30-day non-conversion.
          </p>
          <div className="h-56">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={barrierRows} layout="vertical" margin={{ left: 80 }}>
                <XAxis type="number" tick={{ fontSize: 11 }} />
                <YAxis type="category" dataKey="name" tick={{ fontSize: 11 }} width={80} />
                <Tooltip />
                <Bar dataKey="value" fill="#44403c" radius={[0, 4, 4, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </Card>
      </div>

      <div className="mt-8">
        <div className="mb-3 flex items-end justify-between">
          <h3 className="text-sm font-semibold">Top 5 opportunity areas</h3>
          <Link href="/opportunities" className="text-sm text-rose-800 underline">
            Open landscape
          </Link>
        </div>
        <div className="space-y-3">
          {(data.top_opportunities || []).map((opp) => (
            <Link key={opp.opportunity_id} href={`/opportunities/${opp.opportunity_id}`}>
              <Card className="p-4 hover:border-rose-200">
                <div className="flex flex-wrap items-start justify-between gap-3">
                  <div className="max-w-3xl">
                    <p className="text-xs text-zinc-500">#{opp.rank}</p>
                    <p className="font-medium leading-6">{opp.title}</p>
                  </div>
                  <div className="flex gap-2">
                    <Badge>freq {opp.frequency}</Badge>
                    <Badge tone="rose">purchase assoc. {opp.purchase_association}</Badge>
                    <Badge tone="amber">{opp.confidence}</Badge>
                  </div>
                </div>
              </Card>
            </Link>
          ))}
        </div>
      </div>

      <p className="mt-8 text-xs text-zinc-500">{data.quality?.disclaimer}</p>
    </div>
  );
}
