"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { DatasetBanner, PageHeader } from "@/components/layout/shell";
import { Badge, Card } from "@/components/ui/primitives";
import { api, type Banner } from "@/lib/api";

type Hypothesis = {
  hypothesis_id: string;
  hypothesis_name: string;
  statement: string;
  status: string;
  evidence_label: string;
  support_count: number;
  counter_count: number;
  purchase_association: number;
  confidence: string;
  priority: number;
  candidate_opportunity: boolean;
  reasoning: string;
};

type ComparisonRow = {
  hypothesis_id: string;
  hypothesis_name: string;
  evidence: string;
  support: number;
  counter_evidence: number;
  purchase_association: number;
  confidence: string;
  priority: number;
  status: string;
};

type Payload = {
  banner?: Banner;
  hypotheses: Hypothesis[];
  comparison: ComparisonRow[];
};

const STATUS: Record<string, { label: string; tone: "emerald" | "amber" | "rose" | "zinc" }> = {
  supported: { label: "Supported", tone: "emerald" },
  weakly_supported: { label: "Weakly supported", tone: "amber" },
  contradicted: { label: "Contradicted", tone: "rose" },
  insufficient_evidence: { label: "Insufficient evidence", tone: "zinc" },
};

export default function HypothesesPage() {
  const [data, setData] = useState<Payload | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    api<Payload>("/api/hypotheses")
      .then(setData)
      .catch((e: Error) => setError(e.message));
  }, []);

  if (error) {
    return (
      <Card className="p-5">
        <p className="font-medium">Could not load hypotheses.</p>
        <p className="mt-2 text-sm text-zinc-600">{error}</p>
      </Card>
    );
  }
  if (!data) return <p className="text-sm text-zinc-500">Loading hypothesis tests…</p>;

  const ordered = [...(data.hypotheses || [])].sort((a, b) => a.hypothesis_id.localeCompare(b.hypothesis_id));
  const table: ComparisonRow[] = data.comparison?.length
    ? data.comparison
    : ordered.map((hypothesis) => ({
        hypothesis_id: hypothesis.hypothesis_id,
        hypothesis_name: hypothesis.hypothesis_name,
        evidence: hypothesis.evidence_label,
        support: hypothesis.support_count,
        counter_evidence: hypothesis.counter_count,
        purchase_association: hypothesis.purchase_association,
        confidence: hypothesis.confidence,
        priority: hypothesis.priority,
        status: hypothesis.status,
      }));

  return (
    <div>
      <DatasetBanner banner={data.banner} />
      <PageHeader
        title="Hypothesis Testing"
        description="Six starting guesses about wishlist → 30-day conversion. They are not findings. Status is calculated from classified public comments. The engine is allowed to reject them."
      />

      <div className="grid gap-4 md:grid-cols-2">
        {ordered.map((h) => {
          const st = STATUS[h.status] || STATUS.insufficient_evidence;
          return (
            <Link key={h.hypothesis_id} href={`/hypotheses/${h.hypothesis_id}`}>
              <Card className="h-full p-5 hover:border-rose-200">
                <div className="flex items-start justify-between gap-3">
                  <p className="text-xs font-medium uppercase tracking-wide text-rose-800">
                    {h.hypothesis_id} · priority {h.priority}
                  </p>
                  <Badge tone={st.tone}>{st.label}</Badge>
                </div>
                <h3 className="mt-2 font-semibold">{h.hypothesis_name}</h3>
                <p className="mt-2 text-sm leading-6 text-zinc-600">{h.statement}</p>
                <div className="mt-4 flex flex-wrap gap-2 text-xs">
                  <Badge>support {h.support_count}</Badge>
                  <Badge tone="rose">counter {h.counter_count}</Badge>
                  <Badge tone="amber">purchase assoc. {h.purchase_association}%</Badge>
                  <Badge tone="sky">{h.confidence} confidence</Badge>
                </div>
                {h.candidate_opportunity ? (
                  <p className="mt-3 text-xs font-medium text-emerald-800">Candidate opportunity</p>
                ) : (
                  <p className="mt-3 text-xs text-zinc-500">Not promoted to a candidate opportunity</p>
                )}
              </Card>
            </Link>
          );
        })}
      </div>

      <h3 className="mb-3 mt-10 text-sm font-semibold">Comparison</h3>
      <p className="mb-3 text-xs text-zinc-500">
        Frequency is not importance. Purchase association is how often supporting comments also show postponement, abandonment, or buying elsewhere.
      </p>
      <Card className="overflow-x-auto">
        <table className="min-w-full text-left text-sm">
          <thead className="border-b bg-zinc-50 text-xs uppercase text-zinc-500">
            <tr>
              <th className="px-3 py-2">Hypothesis</th>
              <th className="px-3 py-2">Evidence</th>
              <th className="px-3 py-2">Support</th>
              <th className="px-3 py-2">Counter evidence</th>
              <th className="px-3 py-2">Purchase association</th>
              <th className="px-3 py-2">Confidence</th>
              <th className="px-3 py-2">Priority</th>
            </tr>
          </thead>
          <tbody>
            {table.map((row) => (
              <tr key={row.hypothesis_id} className="border-b last:border-0">
                <td className="px-3 py-3">
                  <Link className="font-medium text-rose-900 hover:underline" href={`/hypotheses/${row.hypothesis_id}`}>
                    {row.hypothesis_id} {row.hypothesis_name}
                  </Link>
                </td>
                <td className="px-3 py-3">{row.evidence}</td>
                <td className="px-3 py-3 tabular-nums">{row.support}</td>
                <td className="px-3 py-3 tabular-nums">{row.counter_evidence}</td>
                <td className="px-3 py-3 tabular-nums">{row.purchase_association}%</td>
                <td className="px-3 py-3">{row.confidence}</td>
                <td className="px-3 py-3 tabular-nums">{row.priority}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </Card>
    </div>
  );
}
