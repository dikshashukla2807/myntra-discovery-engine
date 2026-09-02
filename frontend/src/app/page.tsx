"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { DatasetBanner, PageHeader } from "@/components/layout/shell";
import { Badge, Button, Card } from "@/components/ui/primitives";
import { api, type Banner } from "@/lib/api";

type Overview = {
  banner?: Banner;
  demo_available?: boolean;
  coverage_note?: string;
  funnel?: Record<string, number>;
  hypotheses_summary?: {
    tested?: number;
    supported?: number;
    weakly_supported?: number;
    contradicted?: number;
    insufficient_evidence?: number;
  };
  unexplained_relevant?: number;
  top_opportunities?: Array<{
    opportunity_id: string;
    rank: number;
    title: string;
    frequency: number;
    frequency_percentage: number;
    purchase_association: number;
    confidence: string;
    origin?: string;
    source_hypothesis?: string | null;
  }>;
  quality?: {
    source_distribution?: { collected?: Record<string, number>; relevant?: Record<string, number> };
    disclaimer?: string;
    coverage_note?: string;
    duplicates_and_low_value_removed?: number;
    irrelevant_removed?: number;
    relevant?: number;
    total_collected?: number;
  };
};

export default function OverviewPage() {
  const [data, setData] = useState<Overview | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [switching, setSwitching] = useState(false);

  function load() {
    api<Overview>("/api/overview")
      .then(setData)
      .catch((err: Error) => setError(err.message));
  }

  useEffect(() => {
    load();
  }, []);

  async function switchMode(mode: "public" | "demo") {
    setSwitching(true);
    try {
      await api("/api/dataset/mode", { method: "POST", body: JSON.stringify({ mode }) });
      setError(null);
      load();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Could not switch dataset");
    } finally {
      setSwitching(false);
    }
  }

  if (error && !data?.funnel) {
    return (
      <Card className="p-6">
        <p className="font-medium">No processed dataset yet.</p>
        <p className="mt-2 text-sm text-zinc-600">{error}</p>
      </Card>
    );
  }
  if (!data?.funnel) {
    return <p className="text-sm text-zinc-500">Loading overview…</p>;
  }

  const collected = data.quality?.source_distribution?.collected || {};
  const funnel = [
    ["Collected", data.funnel.collected],
    ["Duplicates / low-value removed", data.funnel.duplicates_removed],
    ["Irrelevant removed", data.funnel.irrelevant_removed],
    ["Relevant", data.funnel.relevant],
    ["Purchase-related", data.funnel.purchase_related],
    ["Wishlist-related", data.funnel.wishlist_related],
  ];

  return (
    <div>
      <div className="mb-4 flex flex-wrap gap-2">
        <Button variant={data.banner?.mode === "public" ? "primary" : "outline"} disabled={switching} onClick={() => switchMode("public")}>
          Public-source dataset
        </Button>
        <Button variant={data.banner?.mode === "demo" ? "primary" : "outline"} disabled={switching || !data.demo_available} onClick={() => switchMode("demo")}>
          Demo / sample data
        </Button>
      </div>
      <PageHeader
        eyebrow="Business metric"
        title="Why don’t wishlisted items convert within 30 days?"
        description="Growth wants more users to buy at least one wishlisted item within 30 days — without monetary incentives. We started with six hypotheses, tested them on public comments, and still look for emerging themes. This engine does not pick a solution."
      />

      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
        {funnel.map(([label, value]) => (
          <Card key={String(label)} className="p-4">
            <p className="text-xs uppercase tracking-wide text-zinc-500">{label}</p>
            <p className="mt-2 text-3xl font-semibold tabular-nums">{value ?? 0}</p>
          </Card>
        ))}
      </div>

      <Card className="mt-6 p-5">
        <h3 className="text-sm font-semibold">Source counts (collected)</h3>
        <div className="mt-3 grid gap-3 sm:grid-cols-4 text-sm">
          <p>Google Play: <span className="font-semibold tabular-nums">{collected.google_play ?? 0}</span></p>
          <p>Reddit: <span className="font-semibold tabular-nums">{collected.reddit ?? 0}</span></p>
          <p>YouTube: <span className="font-semibold tabular-nums">{collected.youtube ?? 0}</span></p>
          {(collected.app_store || 0) > 0 ? (
            <p>App Store (optional): <span className="font-semibold tabular-nums">{collected.app_store}</span></p>
          ) : (
            <p className="text-zinc-500">App Store: not in default workflow</p>
          )}
        </div>
        <p className="mt-3 text-xs text-zinc-500">
          YouTube is 0 unless a public export or API key was used. Missing records are not fabricated.
        </p>
      </Card>

      <Card className="mt-6 p-5">
        <h3 className="text-sm font-semibold">Initial hypotheses tested</h3>
        <div className="mt-3 grid gap-3 sm:grid-cols-5 text-sm">
          <p>Tested: <span className="font-semibold tabular-nums">{data.hypotheses_summary?.tested ?? 6}</span></p>
          <p>Supported: <span className="font-semibold tabular-nums">{data.hypotheses_summary?.supported ?? 0}</span></p>
          <p>Weakly supported: <span className="font-semibold tabular-nums">{data.hypotheses_summary?.weakly_supported ?? 0}</span></p>
          <p>Contradicted: <span className="font-semibold tabular-nums">{data.hypotheses_summary?.contradicted ?? 0}</span></p>
          <p>Insufficient evidence: <span className="font-semibold tabular-nums">{data.hypotheses_summary?.insufficient_evidence ?? 0}</span></p>
        </div>
        <p className="mt-3 text-xs text-zinc-500">
          Status is calculated from classified comments. A common keyword (for example “price”) is not enough to support a hypothesis.
          {typeof data.unexplained_relevant === "number" ? ` ${data.unexplained_relevant} relevant comments did not support any of the six starting hypotheses.` : ""}
        </p>
        <Link href="/hypotheses" className="mt-3 inline-block text-sm text-rose-800 underline">
          Open hypothesis testing
        </Link>
      </Card>

      <Card className="mt-4 p-5 text-sm leading-6 text-zinc-700">
        {data.coverage_note || data.quality?.coverage_note}
      </Card>

      <div className="mt-8">
        <div className="mb-3 flex items-end justify-between">
          <h3 className="text-sm font-semibold">Top candidate opportunities</h3>
          <Link href="/opportunities" className="text-sm text-rose-800 underline">
            Full landscape
          </Link>
        </div>
        <div className="space-y-3">
          {(data.top_opportunities || []).map((opp) => (
            <Link key={opp.opportunity_id} href={`/opportunities/${opp.opportunity_id}`}>
              <Card className="p-4 hover:border-rose-200">
                <div className="flex flex-wrap items-start justify-between gap-3">
                  <div className="max-w-3xl">
                    <p className="text-xs text-zinc-500">
                      #{opp.rank}
                      {opp.origin === "emerging"
                        ? " · Emerging opportunity"
                        : opp.source_hypothesis
                          ? ` · ${opp.source_hypothesis}`
                          : ""}
                    </p>
                    <p className="font-medium leading-6">{opp.title}</p>
                  </div>
                  <div className="flex gap-2">
                    <Badge>freq {opp.frequency}</Badge>
                    <Badge tone="rose">{opp.frequency_percentage}% relevant</Badge>
                    <Badge tone="amber">purchase assoc. {opp.purchase_association}</Badge>
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
