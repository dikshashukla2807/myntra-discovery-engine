"use client";

import { Suspense, useEffect, useMemo, useState } from "react";
import { useSearchParams } from "next/navigation";
import { DatasetBanner, PageHeader } from "@/components/layout/shell";
import { Badge, Button, Card } from "@/components/ui/primitives";
import { api, type Banner } from "@/lib/api";

type Row = {
  observation: {
    observation_id: string;
    source: string;
    source_url: string;
    date?: string;
    rating?: number;
    text_original: string;
    dataset_label?: string;
  };
  extraction?: {
    user_intent?: string;
    wishlist_behavior?: string;
    purchase_outcome?: string;
    barriers?: string[];
    uncertainty_description?: string;
    workaround_type?: string[];
    consider_reasons?: string[];
    confidence?: number;
  };
  theme?: { theme_id: string; theme_name: string };
  hypothesis_stances?: Record<string, { stance?: string }>;
};

function EvidenceInner() {
  const params = useSearchParams();
  const [q, setQ] = useState("");
  const [source, setSource] = useState("");
  const [intent, setIntent] = useState("");
  const [outcome, setOutcome] = useState("");
  const [barrier, setBarrier] = useState("");
  const [theme, setTheme] = useState("");
  const [hypothesis, setHypothesis] = useState(params.get("hypothesis") || "");
  const [stance, setStance] = useState(params.get("stance") || "");
  const [offset, setOffset] = useState(0);
  const [total, setTotal] = useState(0);
  const [rows, setRows] = useState<Row[]>([]);
  const [banner, setBanner] = useState<Banner>();
  const [loading, setLoading] = useState(true);

  const query = useMemo(() => {
    const p = new URLSearchParams();
    if (q) p.set("q", q);
    if (source) p.set("source", source);
    if (intent) p.set("user_intent", intent);
    if (outcome) p.set("purchase_outcome", outcome);
    if (barrier) p.set("barrier", barrier);
    if (theme) p.set("theme", theme);
    if (hypothesis) p.set("hypothesis", hypothesis);
    if (stance) p.set("stance", stance);
    p.set("limit", "25");
    p.set("offset", String(offset));
    return p.toString();
  }, [q, source, intent, outcome, barrier, theme, hypothesis, stance, offset]);

  useEffect(() => {
    setLoading(true);
    api<{ total: number; results: Row[] }>(`/api/observations?${query}`)
      .then((d) => {
        setTotal(d.total);
        setRows(d.results);
      })
      .finally(() => setLoading(false));
    api<Banner>("/api/banner").then(setBanner).catch(() => undefined);
  }, [query]);

  return (
    <div>
      <PageHeader
        title="Evidence Explorer"
        description="Original public text, extraction, theme, and source URL. Quotes are never fabricated."
      />
      <div className="mb-4 grid gap-2 md:grid-cols-3">
        <label className="text-xs text-zinc-600">
          Search original text
          <input value={q} onChange={(e) => { setOffset(0); setQ(e.target.value); }} className="mt-1 w-full rounded-md border border-zinc-300 bg-white px-3 py-2 text-sm" />
        </label>
        <label className="text-xs text-zinc-600">
          Source
          <select className="mt-1 w-full rounded-md border border-zinc-300 bg-white px-3 py-2 text-sm" value={source} onChange={(e) => { setOffset(0); setSource(e.target.value); }}>
            <option value="">All sources</option>
            <option value="google_play">Google Play</option>
            <option value="reddit">Reddit</option>
            <option value="youtube">YouTube</option>
            <option value="app_store">App Store</option>
          </select>
        </label>
        <label className="text-xs text-zinc-600">
          User intent
          <select className="mt-1 w-full rounded-md border border-zinc-300 bg-white px-3 py-2 text-sm" value={intent} onChange={(e) => { setOffset(0); setIntent(e.target.value); }}>
            <option value="">All intents</option>
            {["consideration", "wishlist/save", "comparison", "purchase intent", "post-purchase", "postponed", "abandoned", "return/exchange"].map((x) => (
              <option key={x}>{x}</option>
            ))}
          </select>
        </label>
        <label className="text-xs text-zinc-600">
          Purchase outcome
          <select className="mt-1 w-full rounded-md border border-zinc-300 bg-white px-3 py-2 text-sm" value={outcome} onChange={(e) => { setOffset(0); setOutcome(e.target.value); }}>
            <option value="">All outcomes</option>
            {["purchased", "postponed", "abandoned", "purchased alternative", "still considering", "unknown"].map((x) => (
              <option key={x}>{x}</option>
            ))}
          </select>
        </label>
        <label className="text-xs text-zinc-600">
          Barrier
          <select className="mt-1 w-full rounded-md border border-zinc-300 bg-white px-3 py-2 text-sm" value={barrier} onChange={(e) => { setOffset(0); setBarrier(e.target.value); }}>
            <option value="">All barriers</option>
            {["fit", "size", "quality uncertainty", "price", "reviews/trust", "comparison", "product information", "return concern"].map((x) => (
              <option key={x}>{x}</option>
            ))}
          </select>
        </label>
        <label className="text-xs text-zinc-600">
          Hypothesis
          <select className="mt-1 w-full rounded-md border border-zinc-300 bg-white px-3 py-2 text-sm" value={hypothesis} onChange={(e) => { setOffset(0); setHypothesis(e.target.value); }}>
            <option value="">All hypotheses</option>
            {["H1", "H2", "H3", "H4", "H5", "H6"].map((x) => (
              <option key={x}>{x}</option>
            ))}
          </select>
        </label>
        <label className="text-xs text-zinc-600">
          Supporting / counter
          <select className="mt-1 w-full rounded-md border border-zinc-300 bg-white px-3 py-2 text-sm" value={stance} onChange={(e) => { setOffset(0); setStance(e.target.value); }}>
            <option value="">Any stance</option>
            <option value="supporting">Supporting</option>
            <option value="counter">Counter</option>
            <option value="unclear">Unclear</option>
            <option value="neutral">Neutral / not about this hypothesis</option>
          </select>
        </label>
        <label className="text-xs text-zinc-600">
          Theme
          <input value={theme} onChange={(e) => { setOffset(0); setTheme(e.target.value); }} placeholder="Filter by theme text" className="mt-1 w-full rounded-md border border-zinc-300 bg-white px-3 py-2 text-sm" />
        </label>
      </div>
      <p className="mb-3 text-sm text-zinc-500">{loading ? "Loading…" : `${total} matching relevant observations`}</p>
      {!loading && total === 0 ? (
        <Card className="p-5">
          <p className="font-medium">No matching comments.</p>
          <p className="mt-2 text-sm text-zinc-600">Clear filters, or switch dataset on Overview if you expected demo samples.</p>
        </Card>
      ) : null}
      <div className="space-y-3">
        {rows.map((row) => (
          <Card key={row.observation.observation_id} className="p-4">
            <div className="flex flex-wrap items-center gap-2 text-xs text-zinc-500">
              <Badge>{row.observation.source}</Badge>
              {row.observation.dataset_label === "demo_sample" ? <Badge tone="amber">DEMO / SAMPLE DATA</Badge> : <Badge tone="emerald">Public-source</Badge>}
              <span>{row.observation.date?.slice(0, 10)}</span>
              <span>{row.observation.observation_id}</span>
            </div>
            <p className="mt-2 whitespace-pre-wrap text-sm leading-6 text-zinc-800">{row.observation.text_original}</p>
            <div className="mt-3 grid gap-2 text-xs text-zinc-600 md:grid-cols-2">
              <p><span className="font-medium">Why considered:</span> {(row.extraction?.consider_reasons || []).join(", ") || "—"}</p>
              <p><span className="font-medium">After consideration:</span> {row.extraction?.purchase_outcome || "—"}</p>
              <p><span className="font-medium">Barrier:</span> {(row.extraction?.barriers || []).join(", ") || "—"}</p>
              <p><span className="font-medium">Workaround:</span> {(row.extraction?.workaround_type || []).join(", ") || "—"}</p>
              <p className="md:col-span-2"><span className="font-medium">Uncertainty:</span> {row.extraction?.uncertainty_description || "—"}</p>
              <p className="md:col-span-2"><span className="font-medium">Theme:</span> {row.theme?.theme_name || "—"}</p>
            </div>
            {row.observation.source_url ? (
              <a className="mt-3 inline-block text-sm text-rose-800 underline" href={row.observation.source_url} target="_blank" rel="noreferrer">
                Open original source
              </a>
            ) : null}
          </Card>
        ))}
      </div>
      <div className="mt-4 flex gap-2">
        <Button variant="outline" disabled={offset === 0} onClick={() => setOffset(Math.max(0, offset - 25))}>Previous</Button>
        <Button variant="outline" disabled={offset + 25 >= total} onClick={() => setOffset(offset + 25)}>Next</Button>
      </div>
    </div>
  );
}

export default function EvidencePage() {
  return (
    <Suspense fallback={<p className="text-sm text-zinc-500">Loading evidence…</p>}>
      <EvidenceInner />
    </Suspense>
  );
}
