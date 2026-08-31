import { NextResponse } from "next/server";
import { currentMode, datasetBanner, loadExtractions, loadHypotheses, loadRelevant, packEvidence } from "@/lib/dataset";

export const dynamic = "force-dynamic";

export async function GET(_request: Request, ctx: { params: Promise<{ id: string }> }) {
  try {
    const { id } = await ctx.params;
    const mode = await currentMode();
    const match = loadHypotheses(mode).find(
      (row) => String(row.hypothesis_id).toLowerCase() === id.toLowerCase(),
    );
    if (!match) return NextResponse.json({ error: "Hypothesis not found" }, { status: 404 });
    const obs = Object.fromEntries(loadRelevant(mode).map((row) => [String(row.observation_id), row]));
    const ext = loadExtractions(mode);
    return NextResponse.json({
      hypothesis: match,
      supporting: packEvidence(match.supporting_observations as string[] | undefined, obs, ext, 25),
      counter: packEvidence(match.counter_observations as string[] | undefined, obs, ext, 25),
      banner: datasetBanner(mode),
    });
  } catch (err) {
    const message = err instanceof Error ? err.message : "Internal Server Error";
    return NextResponse.json({ error: message }, { status: 500 });
  }
}
