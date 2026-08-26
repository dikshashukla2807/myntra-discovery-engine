"use client";

import { useEffect, useState } from "react";
import { useSearchParams } from "next/navigation";
import { DatasetBanner, PageHeader } from "@/components/layout/shell";
import { Button, Card } from "@/components/ui/primitives";
import { api, type Banner } from "@/lib/api";
import { Suspense } from "react";

type Opp = { opportunity_id: string; title: string; user_segment?: string[] };
type Plan = {
  selected_opportunity: string;
  target_segment: string;
  research_objective: string;
  interview_questions: string[];
  notes: string[];
  claim_type: string;
};

function PlannerInner() {
  const params = useSearchParams();
  const [opps, setOpps] = useState<Opp[]>([]);
  const [opportunityId, setOpportunityId] = useState(params.get("opportunity") || "");
  const [segment, setSegment] = useState("");
  const [plan, setPlan] = useState<Plan | null>(null);
  const [banner, setBanner] = useState<Banner>();

  useEffect(() => {
    api<Opp[]>("/api/opportunities").then((rows) => {
      setOpps(rows);
      setOpportunityId((id) => id || rows[0]?.opportunity_id || "");
    });
    api<Banner>("/api/banner").then(setBanner).catch(() => undefined);
  }, []);

  async function generate() {
    const result = await api<Plan>("/api/interviews", {
      method: "POST",
      body: JSON.stringify({ opportunity_id: opportunityId, segment: segment || undefined }),
    });
    setPlan(result);
  }

  return (
    <div>
      <DatasetBanner banner={banner} />
      <PageHeader
        title="Interview planner"
        description="Questions are about past behavior. They do not ask whether someone would use a feature. The engine identifies opportunity areas; interviews validate the problem."
      />
      <Card className="mb-6 space-y-3 p-5">
        <label className="block text-sm">
          Opportunity
          <select value={opportunityId} onChange={(e) => setOpportunityId(e.target.value)} className="mt-1 w-full rounded-md border border-zinc-300 bg-white px-3 py-2">
            {opps.map((o) => <option key={o.opportunity_id} value={o.opportunity_id}>{o.title}</option>)}
          </select>
        </label>
        <label className="block text-sm">
          Target segment (optional)
          <input value={segment} onChange={(e) => setSegment(e.target.value)} className="mt-1 w-full rounded-md border border-zinc-300 bg-white px-3 py-2" placeholder="e.g. fit-conscious shoppers" />
        </label>
        <Button onClick={generate}>Generate 8–12 behavioral questions</Button>
      </Card>
      {plan ? (
        <Card className="p-5">
          <p className="text-xs uppercase text-rose-800">{plan.claim_type}</p>
          <h3 className="mt-1 font-semibold">{plan.selected_opportunity}</h3>
          <p className="mt-2 text-sm text-zinc-600">Segment: {plan.target_segment}</p>
          <p className="mt-2 text-sm leading-6">{plan.research_objective}</p>
          <ol className="mt-4 list-decimal space-y-2 pl-5 text-sm leading-6">
            {plan.interview_questions.map((q) => <li key={q}>{q}</li>)}
          </ol>
          <ul className="mt-4 list-disc pl-5 text-xs text-zinc-500">
            {plan.notes.map((n) => <li key={n}>{n}</li>)}
          </ul>
        </Card>
      ) : null}
    </div>
  );
}

export default function InterviewsPage() {
  return (
    <Suspense fallback={<p className="text-sm text-zinc-500">Loading planner…</p>}>
      <PlannerInner />
    </Suspense>
  );
}
