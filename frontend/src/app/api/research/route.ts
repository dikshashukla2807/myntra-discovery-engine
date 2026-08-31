import { NextResponse } from "next/server";
import { currentMode, datasetBanner, interviewPlan, loadOpportunities } from "@/lib/dataset";

export const dynamic = "force-dynamic";

export async function GET(request: Request) {
  try {
    const opportunityId = new URL(request.url).searchParams.get("opportunity_id") || "";
    const mode = await currentMode();
    const opps = loadOpportunities(mode);
    if (!opps.length) return NextResponse.json({ error: "No opportunities yet" }, { status: 404 });
    const match = opportunityId ? opps.find((o) => o.opportunity_id === opportunityId) : opps[0];
    if (!match) return NextResponse.json({ error: "Opportunity not found" }, { status: 404 });
    const segs = (match.user_segment as string[] | undefined) || [];
    const segment = segs[0] && segs[0] !== "Insufficient evidence." ? segs[0] : null;
    const plan = interviewPlan(match, segment) as Record<string, unknown>;
    plan.opportunities = opps.map((o) => ({
      opportunity_id: o.opportunity_id,
      rank: o.rank,
      title: o.title,
    }));
    plan.end_state = "READY FOR PRIMARY RESEARCH";
    plan.banner = datasetBanner(mode);
    return NextResponse.json(plan);
  } catch (err) {
    const message = err instanceof Error ? err.message : "Internal Server Error";
    return NextResponse.json({ error: message }, { status: 500 });
  }
}
