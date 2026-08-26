"use client";

import { useEffect, useState } from "react";
import { Bar, BarChart, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";
import { DatasetBanner, PageHeader } from "@/components/layout/shell";
import { Card } from "@/components/ui/primitives";
import { api, type Banner } from "@/lib/api";

type Signals = {
  user_intent?: Record<string, number>;
  purchase_outcomes?: Record<string, number>;
  why_consider_or_save?: Record<string, number>;
  barriers?: Record<string, number>;
  workarounds?: Record<string, number>;
  external_research_count?: number;
  external_research_pct?: number;
};

function ChartBlock({ title, hint, data }: { title: string; hint: string; data: Record<string, number> | undefined }) {
  const rows = Object.entries(data || {}).map(([name, value]) => ({ name, value }));
  return (
    <Card className="p-5">
      <h3 className="text-sm font-semibold">{title}</h3>
      <p className="mb-4 mt-1 text-xs text-zinc-500">{hint}</p>
      {rows.length === 0 ? (
        <p className="text-sm text-zinc-500">No extracted signal in the current dataset.</p>
      ) : (
        <div className="h-64">
          <ResponsiveContainer width="100%" height="100%">
            <BarChart data={rows} layout="vertical" margin={{ left: 90 }}>
              <XAxis type="number" tick={{ fontSize: 11 }} />
              <YAxis type="category" dataKey="name" width={90} tick={{ fontSize: 11 }} />
              <Tooltip />
              <Bar dataKey="value" fill="#9f1239" radius={[0, 4, 4, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </div>
      )}
    </Card>
  );
}

export default function SignalsPage() {
  const [data, setData] = useState<Signals>({});
  const [banner, setBanner] = useState<Banner>();
  useEffect(() => {
    api<Signals>("/api/signals").then(setData).catch(() => undefined);
    api<Banner>("/api/banner").then(setBanner).catch(() => undefined);
  }, []);

  return (
    <div>
      <DatasetBanner banner={banner} />
      <PageHeader
        title="Behavioral Signals"
        description="What public comments say about considering, saving, postponing, abandoning, researching elsewhere, and working around uncertainty. Labels are assigned only when the original text supports them."
      />
      <div className="mb-6 grid gap-4 sm:grid-cols-2">
        <Card className="p-4">
          <p className="text-xs uppercase text-zinc-500">External research mentioned</p>
          <p className="mt-2 text-3xl font-semibold">{data.external_research_pct ?? 0}%</p>
          <p className="mt-1 text-xs text-zinc-500">{data.external_research_count ?? 0} relevant observations</p>
        </Card>
        <Card className="p-4 text-sm leading-6 text-zinc-600">
          Wishlist language in app reviews is rare. Absence of the word “wishlist” is not evidence that
          users do not save items — it is a coverage gap for primary research.
        </Card>
      </div>
      <div className="grid gap-6 lg:grid-cols-2">
        <ChartBlock title="Why users consider or save" hint="Extracted consider-reasons. Unclear is omitted." data={data.why_consider_or_save} />
        <ChartBlock title="Purchase outcomes in text" hint="Observed language, not a measured conversion rate." data={data.purchase_outcomes} />
        <ChartBlock title="User intent" hint="One primary intent per observation." data={data.user_intent} />
        <ChartBlock title="Workarounds" hint="How users currently reduce uncertainty." data={data.workarounds} />
      </div>
    </div>
  );
}
