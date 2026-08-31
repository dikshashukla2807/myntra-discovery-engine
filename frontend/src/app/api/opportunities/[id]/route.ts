import { NextResponse } from "next/server";
import { currentMode, datasetBanner, loadExtractions, loadOpportunities, loadPipeline, loadRelevant, loadThemes, packEvidence } from "@/lib/dataset";

export const dynamic = "force-dynamic";

export async function GET(_request: Request, ctx: { params: Promise<{ id: string }> }) {
  try {
    const { id } = await ctx.params;
    const mode = await currentMode();
    const match = loadOpportunities(mode).find((row) => row.opportunity_id === id);
    if (!match) return NextResponse.json({ error: "Opportunity not found" }, { status: 404 });
    const themeIds = new Set((match.theme_ids as string[]) || []);
    const themes = loadThemes(mode).filter((t) => themeIds.has(String(t.theme_id)));
    const obs = Object.fromEntries(loadRelevant(mode).map((row) => [String(row.observation_id), row]));
    const ext = loadExtractions(mode);
    return NextResponse.json({
      opportunity: match,
      themes,
      supporting: packEvidence(match.supporting_evidence_ids as string[] | undefined, obs, ext, 20),
      counter: packEvidence(match.counter_evidence_ids as string[] | undefined, obs, ext, 20),
      banner: datasetBanner(mode),
      scoring_weights: (loadPipeline(mode).weights as Record<string, number> | undefined) || undefined,
    });
  } catch (err) {
    const message = err instanceof Error ? err.message : "Internal Server Error";
    return NextResponse.json({ error: message }, { status: 500 });
  }
}
