"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { useParams } from "next/navigation";
import { DatasetBanner, PageHeader } from "@/components/layout/shell";
import { Badge, Card } from "@/components/ui/primitives";
import { api, type Banner } from "@/lib/api";

type Detail = {
  banner?: Banner;
  hypothesis: {
    hypothesis_id: string;
    hypothesis_name: string;
    statement: string;
    status: string;
    evidence_label: string;
    support_count: number;
    counter_count: number;
    unclear_count?: number;
    purchase_association: number;
    purchase_related_support: number;
    confidence: string;
    candidate_opportunity: boolean;
    reasoning: string;
    research_gap: string;
    affected_segments: string[];
    common_workarounds: string[];
    uncertainty_kinds?: string[];
    source_distribution?: Record<string, number>;
  };
  supporting: Array<{
    observation: { observation_id: string; source: string; source_url: string; date?: string; text_original: string };
    extraction?: { purchase_outcome?: string; barriers?: string[] };
  }>;
  counter: Array<{
    observation: { observation_id: string; source: string; source_url: string; date?: string; text_original: string };
  }>;
};

const STATUS: Record<string, string> = {
  supported: "Supported",
  weakly_supported: "Weakly supported",
  contradicted: "Contradicted",
  insufficient_evidence: "Insufficient evidence",
};

export default function HypothesisDetailPage() {
  const params = useParams<{ id: string }>();
  const [data, setData] = useState<Detail | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!params.id) return;
    api<Detail>(`/api/hypotheses/${params.id}`)
      .then(setData)
      .catch((e: Error) => setError(e.message));
  }, [params.id]);

  if (error) return <p className="text-sm text-red-700">{error}</p>;
  if (!data) return <p className="text-sm text-zinc-500">Loading…</p>;
  const h = data.hypothesis;

  return (
    <div>
      <DatasetBanner banner={data.banner} />
      <p className="text-sm">
        <Link className="text-rose-800 underline" href="/hypotheses">← All hypotheses</Link>
      </p>
      <PageHeader eyebrow={h.hypothesis_id} title={h.hypothesis_name} description={h.statement} />

      <div className="mb-6 flex flex-wrap gap-2">
        <Badge tone="rose">{STATUS[h.status] || h.status}</Badge>
        <Badge>Evidence: {h.evidence_label}</Badge>
        <Badge tone="sky">{h.confidence} confidence</Badge>
        {h.candidate_opportunity ? <Badge tone="emerald">Candidate opportunity</Badge> : <Badge>Not a candidate opportunity</Badge>}
      </div>

      <div className="mb-6 grid gap-3 sm:grid-cols-4">
        <Card className="p-4"><p className="text-xs text-zinc-500">Supporting</p><p className="text-2xl font-semibold">{h.support_count}</p></Card>
        <Card className="p-4"><p className="text-xs text-zinc-500">Counter</p><p className="text-2xl font-semibold">{h.counter_count}</p></Card>
        <Card className="p-4"><p className="text-xs text-zinc-500">Purchase association</p><p className="text-2xl font-semibold">{h.purchase_association}%</p><p className="text-xs">{h.purchase_related_support} supporting comments observed alongside postponement / abandonment / alternative purchase</p></Card>
        <Card className="p-4"><p className="text-xs text-zinc-500">Unclear</p><p className="text-2xl font-semibold">{h.unclear_count ?? 0}</p></Card>
      </div>

      <Card className="mb-6 p-5">
        <h3 className="text-sm font-semibold">What the counts say</h3>
        <p className="mt-2 text-sm leading-6">{h.reasoning}</p>
        <p className="mt-3 text-xs text-zinc-500">Numbers are calculated from classified observations. They are not invented.</p>
      </Card>

      {(h.uncertainty_kinds || []).length ? (
        <Card className="mb-6 p-5">
          <h3 className="text-sm font-semibold">Which uncertainty (H6)</h3>
          <div className="mt-2 flex flex-wrap gap-2">
            {h.uncertainty_kinds!.map((k) => <Badge key={k}>{k}</Badge>)}
          </div>
        </Card>
      ) : null}

      <Card className="mb-6 p-5">
        <h3 className="text-sm font-semibold">Research gap</h3>
        <p className="mt-2 text-sm leading-6">{h.research_gap}</p>
        <Link className="mt-3 inline-block text-sm text-rose-800 underline" href={`/evidence?hypothesis=${h.hypothesis_id}&stance=supporting`}>
          Open supporting comments in Evidence Explorer
        </Link>
      </Card>

      <div className="grid gap-6 lg:grid-cols-2">
        <div>
          <h3 className="mb-3 text-sm font-semibold">Supporting evidence</h3>
          {data.supporting.length === 0 ? <p className="text-sm text-zinc-500">Insufficient supporting evidence.</p> : data.supporting.map((row) => (
            <Card key={row.observation.observation_id} className="mb-3 p-4">
              <p className="text-xs text-zinc-500">{row.observation.source} · {row.observation.observation_id}</p>
              <p className="mt-2 text-sm leading-6">{row.observation.text_original}</p>
              <p className="mt-2 text-xs text-zinc-500">Outcome: {row.extraction?.purchase_outcome || "—"}</p>
              <a className="mt-2 inline-block text-xs text-rose-800 underline" href={row.observation.source_url} target="_blank" rel="noreferrer">Original source</a>
            </Card>
          ))}
        </div>
        <div>
          <h3 className="mb-3 text-sm font-semibold">Counter evidence</h3>
          {data.counter.length === 0 ? <p className="text-sm text-zinc-500">Insufficient counter-evidence.</p> : data.counter.map((row) => (
            <Card key={row.observation.observation_id} className="mb-3 p-4">
              <p className="text-xs text-zinc-500">{row.observation.source} · {row.observation.observation_id}</p>
              <p className="mt-2 text-sm leading-6">{row.observation.text_original}</p>
              <a className="mt-2 inline-block text-xs text-rose-800 underline" href={row.observation.source_url} target="_blank" rel="noreferrer">Original source</a>
            </Card>
          ))}
        </div>
      </div>
    </div>
  );
}
