"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { DatasetBanner, PageHeader } from "@/components/layout/shell";
import { Card } from "@/components/ui/primitives";
import { api, type Banner } from "@/lib/api";

type Gap = {
  opportunity_id: string;
  opportunity_title: string;
  research_gap: string;
  unknowns: string[];
  why_primary_research: string;
  claim_type: string;
};

export default function GapsPage() {
  const [rows, setRows] = useState<Gap[]>([]);
  const [banner, setBanner] = useState<Banner>();
  useEffect(() => {
    api<Gap[]>("/api/gaps").then(setRows).catch(() => setRows([]));
    api<Banner>("/api/banner").then(setBanner).catch(() => undefined);
  }, []);

  return (
    <div>
      <DatasetBanner banner={banner} />
      <PageHeader
        title="Research gaps"
        description="Public UGC can show that a theme exists. It cannot prove that the theme causes 30-day wishlist non-conversion. These unknowns become the 5–6 user interviews."
      />
      <div className="space-y-4">
        {rows.map((gap) => (
          <Card key={gap.opportunity_id} className="p-5">
            <p className="text-xs uppercase text-rose-800">{gap.claim_type}</p>
            <h3 className="mt-1 font-semibold">{gap.opportunity_title}</h3>
            <p className="mt-2 text-sm leading-6 text-zinc-700">{gap.research_gap}</p>
            <ul className="mt-3 list-disc space-y-1 pl-5 text-sm text-zinc-700">
              {gap.unknowns.map((u) => <li key={u}>{u}</li>)}
            </ul>
            <p className="mt-3 text-xs text-zinc-500">{gap.why_primary_research}</p>
            <Link className="mt-3 inline-block text-sm text-rose-800 underline" href={`/interviews?opportunity=${gap.opportunity_id}`}>
              Plan interviews
            </Link>
          </Card>
        ))}
      </div>
    </div>
  );
}
