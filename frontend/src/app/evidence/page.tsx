"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { DatasetBanner, PageHeader } from "@/components/layout/shell";
import { Badge, Card } from "@/components/ui/primitives";
import { api, type Banner } from "@/lib/api";

type Opp = { opportunity_id: string; title: string; rank: number };
type Detail = {
  opportunity: { title: string; claim_type: string };
  supporting: Array<{ observation: { observation_id: string; source: string; source_url: string; date?: string; text_original: string }; extraction?: { user_intent?: string; purchase_outcome?: string; wishlist_behavior?: string } }>;
  counter: Array<{ observation: { observation_id: string; source: string; source_url: string; text_original: string } }>;
  themes: Array<{ theme_id: string; theme_name: string }>;
};

export default function EvidencePage() {
  const [opps, setOpps] = useState<Opp[]>([]);
  const [selected, setSelected] = useState("");
  const [detail, setDetail] = useState<Detail | null>(null);
  const [banner, setBanner] = useState<Banner>();

  useEffect(() => {
    api<Opp[]>("/api/opportunities").then((rows) => {
      setOpps(rows);
      if (rows[0]) setSelected(rows[0].opportunity_id);
    });
    api<Banner>("/api/banner").then(setBanner).catch(() => undefined);
  }, []);

  useEffect(() => {
    if (!selected) return;
    api<Detail>(`/api/opportunities/${selected}`).then(setDetail).catch(() => setDetail(null));
  }, [selected]);

  return (
    <div>
      <DatasetBanner banner={banner} />
      <PageHeader
        title="Evidence Explorer"
        description="Opportunity → theme → supporting / counter observations → original source. Every quote is the original public text."
      />
      <select value={selected} onChange={(e) => setSelected(e.target.value)} className="mb-6 w-full rounded-md border border-zinc-300 bg-white px-3 py-2 text-sm">
        {opps.map((o) => (
          <option key={o.opportunity_id} value={o.opportunity_id}>
            #{o.rank} {o.title}
          </option>
        ))}
      </select>
      {detail ? (
        <div>
          <p className="mb-2 text-xs uppercase tracking-wide text-rose-800">{detail.opportunity.claim_type}</p>
          <h3 className="mb-4 font-semibold">{detail.opportunity.title}</h3>
          <div className="mb-4 flex flex-wrap gap-2">
            {detail.themes.map((t) => <Badge key={t.theme_id}>{t.theme_name.slice(0, 80)}…</Badge>)}
          </div>
          <div className="grid gap-6 lg:grid-cols-2">
            <section>
              <h4 className="mb-3 text-sm font-semibold">Supporting</h4>
              {detail.supporting.map((row) => (
                <Card key={row.observation.observation_id} className="mb-3 p-4">
                  <p className="text-xs text-zinc-500">{row.observation.source} · {row.observation.observation_id} · intent {row.extraction?.user_intent}</p>
                  <p className="mt-2 text-sm leading-6">{row.observation.text_original}</p>
                  <a className="mt-2 inline-block text-xs text-rose-800 underline" href={row.observation.source_url} target="_blank" rel="noreferrer">Original source</a>
                </Card>
              ))}
            </section>
            <section>
              <h4 className="mb-3 text-sm font-semibold">Counter</h4>
              {detail.counter.map((row) => (
                <Card key={row.observation.observation_id} className="mb-3 p-4">
                  <p className="text-xs text-zinc-500">{row.observation.source} · {row.observation.observation_id}</p>
                  <p className="mt-2 text-sm leading-6">{row.observation.text_original}</p>
                  <a className="mt-2 inline-block text-xs text-rose-800 underline" href={row.observation.source_url} target="_blank" rel="noreferrer">Original source</a>
                </Card>
              ))}
            </section>
          </div>
          <Link className="mt-4 inline-block text-sm text-rose-800 underline" href={`/opportunities/${selected}`}>
            Open full opportunity analysis
          </Link>
        </div>
      ) : null}
    </div>
  );
}
