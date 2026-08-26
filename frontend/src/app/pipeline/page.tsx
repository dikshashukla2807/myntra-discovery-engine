"use client";

import { useEffect, useState } from "react";
import { DatasetBanner, PageHeader } from "@/components/layout/shell";
import { Badge, Button, Card } from "@/components/ui/primitives";
import { api, type Banner } from "@/lib/api";

type Stage = {
  name: string;
  status: string;
  processed: number;
  successful: number;
  failed: number;
  error?: string | null;
  updated_at?: string;
};

type Pipeline = {
  last_run?: string;
  dataset_label?: string;
  stages?: Stage[];
  note?: string;
};

export default function PipelinePage() {
  const [data, setData] = useState<Pipeline>({});
  const [banner, setBanner] = useState<Banner>();
  const [busy, setBusy] = useState(false);
  const [message, setMessage] = useState("");

  function refresh() {
    api<Pipeline>("/api/pipeline").then(setData).catch(() => setData({}));
    api<Banner>("/api/banner").then(setBanner).catch(() => undefined);
  }

  useEffect(() => {
    refresh();
  }, []);

  async function run(demoOnly: boolean) {
    setBusy(true);
    setMessage(demoOnly ? "Running pipeline on Demo / Sample Data…" : "Re-running pipeline on collected public-source data…");
    try {
      await api("/api/pipeline/run", {
        method: "POST",
        body: JSON.stringify({ demo_only: demoOnly, include_demo: demoOnly }),
      });
      setMessage("Pipeline finished.");
      refresh();
    } catch (err) {
      setMessage(err instanceof Error ? err.message : "Pipeline failed");
    } finally {
      setBusy(false);
    }
  }

  const stages = data.stages || [];

  return (
    <div>
      <DatasetBanner banner={banner} />
      <PageHeader
        title="Pipeline / Data Health"
        description="Collection → cleaning → relevance → extraction → embeddings → clustering → themes → opportunity scoring. Each stage writes artifacts under data/. Already-analyzed observations are not reinvented as source text."
      />
      <div className="mb-6 flex flex-wrap gap-2">
        <Button disabled={busy} onClick={() => run(false)}>Re-run on public-source data</Button>
        <Button variant="outline" disabled={busy} onClick={() => run(true)}>Run Demo Mode</Button>
        <a className="rounded-md border border-zinc-300 bg-white px-3 py-2 text-sm" href="/api/export/analysis.json">Export JSON</a>
        <a className="rounded-md border border-zinc-300 bg-white px-3 py-2 text-sm" href="/api/export/observations.csv">Export observations CSV</a>
      </div>
      {message ? <p className="mb-4 text-sm text-zinc-600">{message}</p> : null}
      <p className="mb-4 text-sm text-zinc-500">Last run: {data.last_run || "never"}</p>
      <div className="grid gap-3">
        {["collection","cleaning","relevance","extraction","embeddings","clustering","themes","opportunity_scoring"].map((name) => {
          const stage = stages.find((s) => s.name === name) || stages.find((s) => s.name.includes(name));
          return (
            <Card key={name} className="flex items-center justify-between p-4">
              <div>
                <p className="font-medium capitalize">{name.replaceAll("_", " ")}</p>
                <p className="text-xs text-zinc-500">{stage?.error || stage?.updated_at || "—"}</p>
              </div>
              <div className="flex items-center gap-2 text-sm">
                <Badge tone={stage?.status === "ok" ? "emerald" : stage?.status === "skipped" ? "amber" : "zinc"}>
                  {stage?.status || "pending"}
                </Badge>
                <span className="tabular-nums text-zinc-600">{stage?.successful ?? 0}/{stage?.processed ?? 0}</span>
                {stage?.failed ? <span className="text-rose-800">{stage.failed} failed</span> : null}
              </div>
            </Card>
          );
        })}
      </div>
      <p className="mt-6 text-xs text-zinc-500">{data.note}</p>
    </div>
  );
}
