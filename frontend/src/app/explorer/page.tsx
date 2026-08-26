"use client";

import { useEffect, useMemo, useState } from "react";
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
    title?: string;
    text_original: string;
    language?: string;
    dataset_label?: string;
  };
  extraction?: {
    user_intent?: string;
    wishlist_behavior?: string;
    purchase_outcome?: string;
    barriers?: string[];
    confidence?: number;
    external_research?: boolean;
  };
  theme?: { theme_id: string; theme_name: string };
};

const FILTERS = [
  ["source", "source"],
  ["user_intent", "user_intent"],
  ["wishlist_behavior", "wishlist_behavior"],
  ["purchase_outcome", "purchase_outcome"],
  ["barrier", "barrier"],
  ["external_research", "external_research"],
] as const;

export default function ExplorerPage() {
  const [q, setQ] = useState("");
  const [source, setSource] = useState("");
  const [intent, setIntent] = useState("");
  const [wishlist, setWishlist] = useState("");
  const [outcome, setOutcome] = useState("");
  const [barrier, setBarrier] = useState("");
  const [external, setExternal] = useState("");
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
    if (wishlist) p.set("wishlist_behavior", wishlist);
    if (outcome) p.set("purchase_outcome", outcome);
    if (barrier) p.set("barrier", barrier);
    if (external) p.set("external_research", external);
    p.set("limit", "25");
    p.set("offset", String(offset));
    return p.toString();
  }, [q, source, intent, wishlist, outcome, barrier, external, offset]);

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
      <DatasetBanner banner={banner} />
      <PageHeader
        title="Data Explorer"
        description="Every relevant observation keeps original text, source URL, extraction, theme, and confidence. Quotes are never fabricated."
      />
      <div className="mb-4 grid gap-2 md:grid-cols-4">
        <input
          value={q}
          onChange={(e) => {
            setOffset(0);
            setQ(e.target.value);
          }}
          placeholder="Search original text"
          className="rounded-md border border-zinc-300 bg-white px-3 py-2 text-sm"
        />
        <select className="rounded-md border border-zinc-300 bg-white px-3 py-2 text-sm" value={source} onChange={(e) => { setOffset(0); setSource(e.target.value); }}>
          <option value="">All sources</option>
          <option value="google_play">Google Play</option>
          <option value="app_store">App Store</option>
          <option value="reddit">Reddit</option>
          <option value="youtube">YouTube</option>
        </select>
        <select className="rounded-md border border-zinc-300 bg-white px-3 py-2 text-sm" value={intent} onChange={(e) => { setOffset(0); setIntent(e.target.value); }}>
          <option value="">All intents</option>
          {["browsing","consideration","wishlist/save","comparison","purchased","postponed","abandoned","unclear"].map((x) => (
            <option key={x}>{x}</option>
          ))}
        </select>
        <select className="rounded-md border border-zinc-300 bg-white px-3 py-2 text-sm" value={outcome} onChange={(e) => { setOffset(0); setOutcome(e.target.value); }}>
          <option value="">All outcomes</option>
          {["purchased","postponed","abandoned","purchased alternative","still considering","unknown"].map((x) => (
            <option key={x}>{x}</option>
          ))}
        </select>
        <select className="rounded-md border border-zinc-300 bg-white px-3 py-2 text-sm" value={wishlist} onChange={(e) => { setOffset(0); setWishlist(e.target.value); }}>
          <option value="">Wishlist behavior</option>
          {["explicitly wishlisted","explicitly saved","implied shortlist","carted as consideration","no evidence"].map((x) => (
            <option key={x}>{x}</option>
          ))}
        </select>
        <select className="rounded-md border border-zinc-300 bg-white px-3 py-2 text-sm" value={barrier} onChange={(e) => { setOffset(0); setBarrier(e.target.value); }}>
          <option value="">Barrier</option>
          {["price","fit","size","quality uncertainty","reviews/trust","return concern","comparison","delivery"].map((x) => (
            <option key={x}>{x}</option>
          ))}
        </select>
        <select className="rounded-md border border-zinc-300 bg-white px-3 py-2 text-sm" value={external} onChange={(e) => { setOffset(0); setExternal(e.target.value); }}>
          <option value="">External research</option>
          <option value="true">Yes</option>
          <option value="false">No</option>
        </select>
      </div>
      <p className="mb-3 text-sm text-zinc-500">{loading ? "Loading…" : `${total} matching relevant observations`}</p>
      <div className="space-y-3">
        {rows.map((row) => (
          <Card key={row.observation.observation_id} className="p-4">
            <div className="flex flex-wrap items-center gap-2 text-xs text-zinc-500">
              <Badge>{row.observation.source}</Badge>
              {row.observation.dataset_label === "demo_sample" ? <Badge tone="amber">Demo / Sample Data</Badge> : <Badge tone="emerald">Public-source</Badge>}
              {row.observation.rating != null ? <span>★ {row.observation.rating}</span> : null}
              <span>{row.observation.date?.slice(0, 10)}</span>
              <span>{row.observation.observation_id}</span>
            </div>
            {row.observation.title ? <p className="mt-2 text-sm font-medium">{row.observation.title}</p> : null}
            <p className="mt-2 whitespace-pre-wrap text-sm leading-6 text-zinc-800">{row.observation.text_original}</p>
            <div className="mt-3 grid gap-2 text-xs text-zinc-600 md:grid-cols-2">
              <p><span className="font-medium">Intent:</span> {row.extraction?.user_intent || "—"}</p>
              <p><span className="font-medium">Wishlist:</span> {row.extraction?.wishlist_behavior || "—"}</p>
              <p><span className="font-medium">Outcome:</span> {row.extraction?.purchase_outcome || "—"}</p>
              <p><span className="font-medium">Barriers:</span> {(row.extraction?.barriers || []).join(", ") || "—"}</p>
              <p className="md:col-span-2"><span className="font-medium">Theme:</span> {row.theme?.theme_name || "—"}</p>
              <p><span className="font-medium">Extraction confidence:</span> {row.extraction?.confidence ?? "—"}</p>
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
        <Button variant="outline" disabled={offset === 0} onClick={() => setOffset(Math.max(0, offset - 25))}>
          Previous
        </Button>
        <Button variant="outline" disabled={offset + 25 >= total} onClick={() => setOffset(offset + 25)}>
          Next
        </Button>
      </div>
      <p className="hidden">{FILTERS.length}</p>
    </div>
  );
}
