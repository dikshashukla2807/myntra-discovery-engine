"use client";

import { useEffect, useState } from "react";
import { DatasetBanner, PageHeader } from "@/components/layout/shell";
import { Card } from "@/components/ui/primitives";
import { api, type Banner } from "@/lib/api";

type Report = {
  title: string;
  dataset_disclaimer: string;
  executive_summary: {
    business_metric: string;
    constraint: string;
    total_observations: number;
    relevant_observations: number;
    top_opportunity_areas: Array<{ rank: number; title: string; score: number; claim_type: string }>;
    key_research_gaps: string[];
    what_this_does_not_answer: string;
  };
};

export default function ReportPage() {
  const [report, setReport] = useState<Report | null>(null);
  const [banner, setBanner] = useState<Banner>();
  useEffect(() => {
    api<Report>("/api/report").then(setReport).catch(() => setReport(null));
    api<Banner>("/api/banner").then(setBanner).catch(() => undefined);
  }, []);

  if (!report?.executive_summary) {
    return <p className="text-sm text-zinc-500">No report generated yet. Run the pipeline.</p>;
  }
  const s = report.executive_summary;
  return (
    <div>
      <DatasetBanner banner={banner} />
      <PageHeader title={report.title} description={report.dataset_disclaimer} />
      <Card className="mb-6 p-5">
        <h3 className="text-sm font-semibold">Executive summary</h3>
        <p className="mt-3 text-sm"><span className="font-medium">Business metric:</span> {s.business_metric}</p>
        <p className="mt-2 text-sm"><span className="font-medium">Constraint:</span> {s.constraint}</p>
        <p className="mt-2 text-sm">Observations: {s.total_observations} · Relevant: {s.relevant_observations}</p>
        <ol className="mt-4 list-decimal space-y-2 pl-5 text-sm">
          {s.top_opportunity_areas.map((o) => (
            <li key={o.rank}><span className="text-xs uppercase text-zinc-500">{o.claim_type}</span> — {o.title}</li>
          ))}
        </ol>
        <p className="mt-4 text-sm italic text-zinc-600">{s.what_this_does_not_answer}</p>
      </Card>
      <Card className="p-5">
        <h3 className="text-sm font-semibold">Key research gaps</h3>
        <ul className="mt-3 list-disc space-y-2 pl-5 text-sm">
          {s.key_research_gaps.map((g) => <li key={g}>{g}</li>)}
        </ul>
        <div className="mt-4 flex gap-3 text-sm">
          <a className="text-rose-800 underline" href="/api/report.html" target="_blank" rel="noreferrer">Open HTML report</a>
          <a className="text-rose-800 underline" href="/api/export/analysis.json">Download JSON</a>
        </div>
      </Card>
    </div>
  );
}
