"use client";

import { Suspense, useEffect, useState } from "react";
import { useSearchParams } from "next/navigation";
import { DatasetBanner, PageHeader } from "@/components/layout/shell";
import { Card } from "@/components/ui/primitives";
import { api, type Banner } from "@/lib/api";

type Plan = {
  banner?: Banner;
  selected_opportunity: string;
  target_segment: string;
  what_we_know: string;
  what_we_dont_know: string;
  research_hypothesis: string;
  research_objective: string;
  interview_questions: string[];
  notes: string[];
  end_state?: string;
  why_primary_research?: string;
  research_objectives?: string[];
  opportunities: Array<{ opportunity_id: string; rank: number; title: string }>;
};

function HandoffInner() {
  const params = useSearchParams();
  const [plan, setPlan] = useState<Plan | null>(null);
  const [opportunityId, setOpportunityId] = useState(params.get("opportunity") || "");
  const [banner, setBanner] = useState<Banner>();

  useEffect(() => {
    const id = opportunityId || params.get("opportunity") || "";
    const qs = id ? `?opportunity_id=${encodeURIComponent(id)}` : "";
    api<Plan>(`/api/research${qs}`).then((p) => {
      setPlan(p);
      setBanner(p.banner);
      if (!opportunityId && p.opportunities?.[0]) {
        setOpportunityId(p.opportunities[0].opportunity_id);
      }
    }).catch(() => setPlan(null));
  }, [opportunityId, params]);

  return (
    <div>
      <DatasetBanner banner={banner} />
      <PageHeader
        title="Research handoff"
        description="Public data can surface a candidate opportunity. It cannot prove the final user problem. This page ends at ready for primary research — not a final solution."
      />
      {plan ? (
        <>
          <label className="mb-6 block text-sm">
            Selected opportunity
            <select
              value={opportunityId}
              onChange={(e) => setOpportunityId(e.target.value)}
              className="mt-1 w-full rounded-md border border-zinc-300 bg-white px-3 py-2"
            >
              {(plan.opportunities || []).map((o) => (
                <option key={o.opportunity_id} value={o.opportunity_id}>
                  #{o.rank} {o.title}
                </option>
              ))}
            </select>
          </label>
          <div className="grid gap-4">
            <Card className="p-5">
              <p className="text-xs uppercase text-zinc-500">Target segment</p>
              <p className="mt-1 text-sm">{plan.target_segment || "Insufficient evidence."}</p>
            </Card>
            <Card className="p-5">
              <h3 className="text-sm font-semibold">What we know</h3>
              <p className="mt-2 text-sm leading-6">{plan.what_we_know}</p>
            </Card>
            <Card className="p-5">
              <h3 className="text-sm font-semibold">What we don’t know</h3>
              <p className="mt-2 text-sm leading-6">{plan.what_we_dont_know}</p>
            </Card>
            <Card className="p-5">
              <h3 className="text-sm font-semibold">Research hypothesis</h3>
              <p className="mt-2 text-sm leading-6">{plan.research_hypothesis}</p>
              <p className="mt-3 text-xs text-zinc-500">{plan.research_objective}</p>
            </Card>
            <Card className="p-5">
              <h3 className="text-sm font-semibold">What we should ask users</h3>
              <ol className="mt-3 list-decimal space-y-2 pl-5 text-sm leading-6">
                {(plan.research_objectives || []).map((q) => <li key={q}>{q}</li>)}
              </ol>
              <p className="mt-3 text-xs text-zinc-500">These are research objectives, not feature-validation questions.</p>
            </Card>
            <Card className="p-5">
              <h3 className="text-sm font-semibold">Interview questions</h3>
              <ol className="mt-3 list-decimal space-y-2 pl-5 text-sm leading-6">
                {plan.interview_questions.map((q) => <li key={q}>{q}</li>)}
              </ol>
              <ul className="mt-4 list-disc pl-5 text-xs text-zinc-500">
                {(plan.notes || []).map((n) => <li key={n}>{n}</li>)}
              </ul>
            </Card>
            <Card className="border-emerald-200 bg-emerald-50 p-5">
              <p className="text-xs font-semibold uppercase tracking-wide text-emerald-900">{plan.end_state || "READY FOR PRIMARY RESEARCH"}</p>
              <p className="mt-2 text-sm leading-6 text-emerald-950">{plan.why_primary_research}</p>
            </Card>
          </div>
        </>
      ) : (
        <p className="text-sm text-zinc-500">Loading handoff…</p>
      )}
    </div>
  );
}

export default function ResearchPage() {
  return (
    <Suspense fallback={<p className="text-sm text-zinc-500">Loading…</p>}>
      <HandoffInner />
    </Suspense>
  );
}
