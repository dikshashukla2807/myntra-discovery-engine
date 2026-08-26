"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { DatasetBanner, PageHeader } from "@/components/layout/shell";
import { Badge, Card } from "@/components/ui/primitives";
import { api, type Banner } from "@/lib/api";

type Seg = {
  segment_id: string;
  name: string;
  definition: string;
  observation_count: number;
  percentage: number;
  major_barriers: string[];
  major_uncertainties: string[];
  workarounds: string[];
  external_research: string[];
  purchase_outcomes: Record<string, number>;
  dominant_opportunity_themes: string[];
  discovered: boolean;
};

export default function SegmentsPage() {
  const [rows, setRows] = useState<Seg[]>([]);
  const [banner, setBanner] = useState<Banner>();
  useEffect(() => {
    api<Seg[]>("/api/segments").then(setRows).catch(() => setRows([]));
    api<Banner>("/api/banner").then(setBanner).catch(() => undefined);
  }, []);

  return (
    <div>
      <DatasetBanner banner={banner} />
      <PageHeader
        title="Behavior-based segments"
        description="Segments are discovered from extraction signals in the text. No demographic segments are invented. A segment only appears if enough observations carry that signal."
      />
      <div className="grid gap-4">
        {rows.map((seg) => (
          <Card key={seg.segment_id} className="p-5">
            <div className="flex flex-wrap items-start justify-between gap-3">
              <div>
                <h3 className="font-semibold">{seg.name}</h3>
                <p className="mt-1 text-sm text-zinc-600">{seg.definition}</p>
              </div>
              <div className="text-right">
                <p className="text-2xl font-semibold tabular-nums">{seg.observation_count}</p>
                <p className="text-xs text-zinc-500">{seg.percentage}% of relevant</p>
              </div>
            </div>
            <div className="mt-4 flex flex-wrap gap-2">
              {seg.major_barriers.map((b) => <Badge key={b} tone="rose">{b}</Badge>)}
              {seg.workarounds.map((b) => <Badge key={b} tone="sky">{b}</Badge>)}
            </div>
            <p className="mt-3 text-xs text-zinc-500">
              Outcomes: {Object.entries(seg.purchase_outcomes || {}).map(([k, v]) => `${k} ${v}`).join(" · ") || "—"}
            </p>
            {seg.dominant_opportunity_themes[0] ? (
              <p className="mt-2 text-sm">Dominant theme: {seg.dominant_opportunity_themes[0]}</p>
            ) : null}
            <Link className="mt-3 inline-block text-sm text-rose-800 underline" href={`/explorer`}>
              Inspect evidence in Data Explorer
            </Link>
          </Card>
        ))}
      </div>
    </div>
  );
}
