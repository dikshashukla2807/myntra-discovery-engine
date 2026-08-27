"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { useParams } from "next/navigation";
import { DatasetBanner, PageHeader } from "@/components/layout/shell";
import { Badge, Card } from "@/components/ui/primitives";
import { api, type Banner } from "@/lib/api";

type Detail = {
  banner?: Banner;
  scoring_weights?: Record<string, number>;
  opportunity: {
    opportunity_id: string;
    rank: number;
    title: string;
    description: string;
    frequency: number;
    frequency_percentage: number;
    purchase_association: number;
    postponement_association: number;
    abandonment_association: number;
    alternative_purchase_association: number;
    evidence_strength: number;
    confidence: string;
    research_gap: string;
    what_we_know?: string;
    existing_workaround: string[];
    user_segment: string[];
    scores: Record<string, number>;
    why_ranked_higher: string;
    scoring_notes: string;
  };
  supporting: Array<{
    observation: { observation_id: string; source: string; source_url: string; date?: string; text_original: string };
    extraction?: { user_intent?: string; purchase_outcome?: string; barriers?: string[] };
  }>;
  counter: Array<{
    observation: { observation_id: string; source: string; source_url: string; date?: string; text_original: string };
  }>;
};

export default function OpportunityDetailPage() {
  const params = useParams<{ id: string }>();
  const [data, setData] = useState<Detail | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!params.id) return;
    api<Detail>(`/api/opportunities/${params.id}`)
      .then(setData)
      .catch((e: Error) => setError(e.message));
  }, [params.id]);

  if (error) return <p className="text-sm text-red-700">{error}</p>;
  if (!data) return <p className="text-sm text-zinc-500">Loading…</p>;
  const o = data.opportunity;
  const segmentText = (o.user_segment || []).join(", ") || "Insufficient evidence.";

  return (
    <div>
      <DatasetBanner banner={data.banner} />
      <p className="text-sm">
        <Link className="text-rose-800 underline" href="/opportunities">← Landscape</Link>
      </p>
      <PageHeader eyebrow={`Rank #${o.rank}`} title={o.title} description={o.description} />

      <Card className="mb-6 p-5">
        <h3 className="text-sm font-semibold">What we observed</h3>
        <p className="mt-2 text-sm leading-6">{o.what_we_know || o.description}</p>
      </Card>

      <div className="mb-6 grid gap-3 sm:grid-cols-4">
        <Card className="p-4"><p className="text-xs text-zinc-500">Frequency</p><p className="text-2xl font-semibold">{o.frequency}</p><p className="text-xs">{o.frequency_percentage}% of relevant</p></Card>
        <Card className="p-4"><p className="text-xs text-zinc-500">Purchase association</p><p className="text-2xl font-semibold">{o.purchase_association}</p><p className="text-xs">postponed {o.postponement_association} · abandoned {o.abandonment_association} · alt {o.alternative_purchase_association}</p></Card>
        <Card className="p-4"><p className="text-xs text-zinc-500">Evidence (1–5)</p><p className="text-2xl font-semibold">{o.evidence_strength}</p></Card>
        <Card className="p-4"><p className="text-xs text-zinc-500">Confidence</p><p className="text-2xl font-semibold">{o.confidence}</p></Card>
      </div>

      <Card className="mb-6 p-5">
        <h3 className="text-sm font-semibold">Why did this rank here?</h3>
        <p className="mt-2 text-sm leading-6 text-zinc-700">{o.why_ranked_higher}</p>
        <p className="mt-3 text-xs text-zinc-500">{o.scoring_notes}</p>
        <div className="mt-4 grid gap-2 sm:grid-cols-2">
          {Object.entries(o.scores || {}).map(([k, v]) => (
            <div key={k} className="flex justify-between text-sm">
              <span className="text-zinc-600">{k.replaceAll("_", " ")}</span>
              <span className="tabular-nums">{v} / 5</span>
            </div>
          ))}
        </div>
      </Card>

      <Card className="mb-6 p-5">
        <h3 className="text-sm font-semibold">Segments</h3>
        <p className="mt-2 text-sm">{segmentText}</p>
        <h3 className="mt-4 text-sm font-semibold">Workarounds</h3>
        <div className="mt-2 flex flex-wrap gap-2">
          {(o.existing_workaround || []).length ? o.existing_workaround.map((s) => <Badge key={s} tone="sky">{s}</Badge>) : <span className="text-sm text-zinc-500">Insufficient evidence.</span>}
        </div>
      </Card>

      <div className="grid gap-6 lg:grid-cols-2">
        <div>
          <h3 className="mb-3 text-sm font-semibold">Supporting evidence</h3>
          {data.supporting.map((row) => (
            <Card key={row.observation.observation_id} className="mb-3 p-4">
              <p className="text-xs text-zinc-500">{row.observation.source} · {row.observation.date?.slice(0, 10)} · {row.observation.observation_id}</p>
              <p className="mt-2 text-sm leading-6">{row.observation.text_original}</p>
              <p className="mt-2 text-xs text-zinc-500">Outcome: {row.extraction?.purchase_outcome || "—"} · Barriers: {(row.extraction?.barriers || []).join(", ") || "—"}</p>
              <a className="mt-2 inline-block text-xs text-rose-800 underline" href={row.observation.source_url} target="_blank" rel="noreferrer">Original source</a>
            </Card>
          ))}
        </div>
        <div>
          <h3 className="mb-3 text-sm font-semibold">Counter evidence</h3>
          <p className="mb-3 text-xs text-zinc-500">Comments that contradict the dominant barrier, or purchased without it. Prevents confirmation bias.</p>
          {data.counter.length === 0 ? <p className="text-sm text-zinc-500">Insufficient counter-evidence.</p> : data.counter.map((row) => (
            <Card key={row.observation.observation_id} className="mb-3 p-4">
              <p className="text-xs text-zinc-500">{row.observation.source} · {row.observation.observation_id}</p>
              <p className="mt-2 text-sm leading-6">{row.observation.text_original}</p>
              <a className="mt-2 inline-block text-xs text-rose-800 underline" href={row.observation.source_url} target="_blank" rel="noreferrer">Original source</a>
            </Card>
          ))}
        </div>
      </div>

      <Card className="mt-6 p-5">
        <h3 className="text-sm font-semibold">Research gap</h3>
        <p className="mt-2 text-sm leading-6">{o.research_gap}</p>
        <Link className="mt-3 inline-block text-sm text-rose-800 underline" href={`/research?opportunity=${o.opportunity_id}`}>
          Open research handoff
        </Link>
      </Card>
    </div>
  );
}
